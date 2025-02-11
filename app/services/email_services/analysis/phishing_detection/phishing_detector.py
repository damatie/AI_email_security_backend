# phishing_detector 
import re
import requests
from transformers import pipeline, RobertaTokenizer, RobertaForSequenceClassification
import base64
import spacy
from email.utils import parseaddr
import tld
import datetime
import whois
from datetime import datetime, timezone
from app.utils.enums import ConfidenceLevelEnum, ThreatSeverityEnum,ThreatTypeEnum
from app.core.config import  Settings


# Load Pretrained RoBERTa Model for Phishing Detection

tokenizer = RobertaTokenizer.from_pretrained(Settings.MODEL_NAME)
model = RobertaForSequenceClassification.from_pretrained(Settings.MODEL_NAME, num_labels=2)
predictor = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Load spaCy for text analysis
nlp = spacy.load("en_core_web_sm")

# VirusTotal API Configuration
VIRUSTOTAL_API_BASE = "https://www.virustotal.com/api/v3"

def extract_urls(text: str):
    """Extract URLs from text content."""
    if not text:
        return []
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    return url_pattern.findall(text)

def check_url_reputation(url: str):
    """Check URL reputation using VirusTotal API."""
    if not url:
        return {
            "url": url,
            "status": "Error",
            "details": "Invalid URL provided"
        }
    
    headers = {
        "accept": "application/json",
        "x-apikey": Settings.VIRUSTOTAL_API_KEY
    }
    
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        analysis_url = f"{VIRUSTOTAL_API_BASE}/urls/{url_id}"
        response = requests.get(analysis_url, headers=headers)
        
        if response.status_code == 404:
            scan_url = f"{VIRUSTOTAL_API_BASE}/urls"
            scan_response = requests.post(scan_url, headers=headers, data={"url": url})
            
            if scan_response.status_code != 200:
                return {
                    "url": url,
                    "status": "Error",
                    "details": f"Failed to submit URL for analysis. Status code: {scan_response.status_code}"
                }
            
            import time
            time.sleep(3)
            response = requests.get(analysis_url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            stats = result.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            harmless = stats.get("harmless", 0)
            
            if malicious > 0:
                return {
                    "url": url,
                    "status": ThreatTypeEnum.MALICIOUS,
                    "details": f"{malicious} security vendors flagged this URL as malicious."
                }
            elif suspicious > 0:
                return {
                    "url": url,
                    "status": ThreatTypeEnum.SUSPICIOUS,
                    "details": f"{suspicious} security vendors flagged this URL as suspicious."
                }
            elif harmless > 0:
                return {
                    "url": url,
                    "status": ThreatTypeEnum.SAFE,
                    "details": f"{harmless} security vendors marked this URL as safe."
                }
        
        return {
            "url": url,
            "status": "Unknown",
            "details": "Could not determine URL status."
        }
        
    except Exception as e:
        return {
            "url": url,
            "status": "Error",
            "details": f"Error analyzing URL: {str(e)}"
        }

def analyze_text_content(text: str):
    """Analyze the text content for common phishing indicators."""
    if not text:
        return {
            "urgency_indicators": [],
            "threat_indicators": [],
            "reward_indicators": [],
            "request_indicators": [],
            "grammar_issues": False,
            "error": "No text content provided"
        }
    
    doc = nlp(text.lower())
    
    # Common phishing keywords and patterns
    urgency_words = {'urgent', 'immediate', 'action required', 'account suspended', 'verify'}
    threat_words = {'suspended', 'terminated', 'blocked', 'unauthorized', 'suspicious'}
    reward_words = {'winner', 'won', 'prize', 'reward', 'congratulations'}
    
    indicators = {
        "urgency_indicators": [],
        "threat_indicators": [],
        "reward_indicators": [],
        "request_indicators": [],
        "grammar_issues": False
    }
    
    text_lower = text.lower()
    
    # Check for matching patterns
    for word in urgency_words:
        if word in text_lower:
            indicators["urgency_indicators"].append(word)
    
    for word in threat_words:
        if word in text_lower:
            indicators["threat_indicators"].append(word)
    
    for word in reward_words:
        if word in text_lower:
            indicators["reward_indicators"].append(word)
    
    # Check for sensitive information requests
    sensitive_patterns = [
        r'(?i)password',
        r'(?i)credit.?card',
        r'(?i)ssn|social.?security',
        r'(?i)bank.?account',
        r'(?i)verify.?identity'
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, text):
            indicators["request_indicators"].append(pattern.replace('(?i)', ''))
    
    # Grammar check
    sentences = [sent for sent in doc.sents]
    if len(sentences) > 3:
        indicators["grammar_issues"] = any(
            len(sent) < 3 or
            not sent[0].text[0].isupper() or
            sum(1 for token in sent if token.is_punct) == 0
            for sent in sentences
        )
    
    return indicators

def get_domain_age(domain):
    """Get domain age and registration details using WHOIS."""
    try:
        w = whois.whois(domain)
        
        # Get creation date
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        if creation_date:
            # Calculate domain age in days
            now = datetime.now(timezone.utc)
            if not creation_date.tzinfo:
                creation_date = creation_date.replace(tzinfo=timezone.utc)
            
            domain_age = (now - creation_date).days
            
            return {
                "age_days": domain_age,
                "creation_date": creation_date.isoformat(),
                "registrar": w.registrar,
                "is_new": domain_age < 30  # Flag domains less than 30 days old
            }
    except Exception as e:
        return {
            "error": f"Could not retrieve WHOIS data: {str(e)}",
            "is_new": True  # Treat errors as suspicious
        }

def analyze_sender_domain(sender: str):
    """Analyze the sender's email domain for suspicious patterns."""
    if not sender:
        return {
            "domain": None,
            "error": "No sender email provided"
        }
    
    _, email = parseaddr(sender)
    domain = email.split('@')[-1] if '@' in email else ''
    
    if not domain:
        return {
            "domain": None,
            "error": "Invalid email format"
        }
    
    try:
        domain_info = tld.get_tld(f"http://{domain}", as_object=True)
        
        suspicious_patterns = [
            'alert', 'security', 'secure', 'bank', 'update', 'verify',
            'account', 'support', 'service'
        ]
        
        contains_suspicious_word = any(
            pattern in domain.lower() for pattern in suspicious_patterns
        )
        
        # Get domain age information
        whois_info = get_domain_age(domain)
        
        return {
            "domain": domain,
            "tld": domain_info.tld,
            "is_suspicious": contains_suspicious_word,
            "is_free_email": domain.lower() in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'],
            "whois_info": whois_info
        }
    except Exception as e:
        return {
            "domain": domain,
            "is_suspicious": True,
            "error": f"Domain analysis error: {str(e)}"
        }

def calculate_risk_score(analysis_results):
    """Calculate a numerical risk score based on all factors with detailed breakdown."""
    score_breakdown = {
        "url_risk": 0,
        "content_risk": 0,
        "domain_risk": 0,
        "total_score": 0
    }
    
    # URL-based risks (max 40 points)
    malicious_urls = sum(1 for result in analysis_results["urls_analyzed"].values() 
                        if result["status"] == "Malicious")
    score_breakdown["url_risk"] = min(malicious_urls * 20, 40)
    
    # Content-based risks (max 40 points)
    content = analysis_results["content_analysis"]
    content_score = 0
    if content["urgency_indicators"]:
        content_score += 10
    if content["threat_indicators"]:
        content_score += 15
    if content["request_indicators"]:
        content_score += 20
    if content["grammar_issues"]:
        content_score += 5
    score_breakdown["content_risk"] = min(content_score, 40)
    
    # Domain analysis (max 20 points)
    domain_score = 0
    sender = analysis_results["sender_analysis"]
    
    if sender.get("is_suspicious", False):
        domain_score += 10
    
    whois_info = sender.get("whois_info", {})
    if whois_info.get("is_new", False):
        domain_score += 10
    elif whois_info.get("error"):
        domain_score += 5
    
    score_breakdown["domain_risk"] = min(domain_score, 20)
    
    # Calculate total score
    score_breakdown["total_score"] = (
        score_breakdown["url_risk"] + 
        score_breakdown["content_risk"] + 
        score_breakdown["domain_risk"]
    )
    
    return score_breakdown

def determine_classification(risk_scores, model_score):
    """Determine final classification based on risk scores and model prediction."""
    total_risk = risk_scores["total_score"]
    model_suggests_phishing = model_score > 0.5
    
    # Risk score thresholds
    HIGH_RISK_THRESHOLD = 40
    MEDIUM_RISK_THRESHOLD = 20
    
    if total_risk >= HIGH_RISK_THRESHOLD:
        return ThreatTypeEnum.PHISHING, ThreatSeverityEnum.HIGH
    elif total_risk >= MEDIUM_RISK_THRESHOLD or model_suggests_phishing:
        return ThreatTypeEnum.SUSPICIOUS, ThreatSeverityEnum.MEDIUM
    else:
        return ThreatTypeEnum.SAFE, ThreatSeverityEnum.LOW

def truncate_text(text: str, max_length: int = 510) -> str:  # Changed from 512 to 510 to account for special tokens
    """
    Truncate text to ensure it doesn't exceed the model's maximum token length.
    Preserves the beginning and end of the text, which often contain important information.
    """
    # First tokenize the text
    tokens = tokenizer.tokenize(text)
    
    if len(tokens) <= max_length:
        return text
    
    # Calculate portions to keep, leaving room for special tokens ([CLS] and [SEP])
    first_portion_size = max_length // 2
    last_portion_size = max_length - first_portion_size
    
    # Keep first and last portions of the text
    first_portion = tokens[:first_portion_size]
    last_portion = tokens[-last_portion_size:]
    
    # Combine portions and convert back to text
    truncated_text = tokenizer.convert_tokens_to_string(first_portion + last_portion)
    
    # Verify the final length is within limits
    final_tokens = tokenizer.encode(truncated_text, add_special_tokens=True)
    if len(final_tokens) > 512:
        # If still too long, reduce further
        return truncate_text(truncated_text, max_length - 10)
    
    return truncated_text

def get_user_friendly_explanation(analysis_results, risk_scores):
    """Generate user-friendly explanations of the risk factors found."""
    risk_factors = []
    content = analysis_results["content_analysis"]
    
    # Urgency language
    if content["urgency_indicators"]:
        risk_factors.append(f"Uses urgency language: {', '.join(content['urgency_indicators'])}")
    
    # Threat language
    if content["threat_indicators"]:
        risk_factors.append(f"Contains threat language: {', '.join(content['threat_indicators'])}")
    
    # Sensitive information requests
    if content["request_indicators"]:
        risk_factors.append(f"Requests sensitive information: {', '.join(content['request_indicators'])}")
    
    # URL analysis
    malicious_urls = sum(1 for result in analysis_results["urls_analyzed"].values() 
                        if result["status"] == "Malicious")
    suspicious_urls = sum(1 for result in analysis_results["urls_analyzed"].values() 
                        if result["status"] == "Suspicious")
    
    if malicious_urls > 0:
        risk_factors.append(f"Contains {malicious_urls} malicious URL(s)")
    if suspicious_urls > 0:
        risk_factors.append(f"Contains {suspicious_urls} suspicious URL(s)")
    
    # Domain analysis
    sender_analysis = analysis_results["sender_analysis"]
    if sender_analysis.get("is_suspicious"):
        risk_factors.append("Suspicious sender domain")
    
    whois_info = sender_analysis.get("whois_info", {})
    if whois_info.get("is_new"):
        risk_factors.append("Sender's domain was registered less than 30 days ago")
    
    if content["grammar_issues"]:
        risk_factors.append("Contains grammar and spelling issues typical of phishing emails")
    
    # Add summary based on risk level
    total_risk = risk_scores["total_score"]
    if total_risk >= 60:
        summary = "This email shows multiple strong indicators of being a phishing attempt"
    elif total_risk >= 40:
        summary = "This email shows several suspicious characteristics that warrant caution"
    elif total_risk >= 20:
        summary = "This email shows some suspicious elements but may be legitimate"
    else:
        summary = "This email shows few or no signs of being malicious"
    
    return {
        "risk_factors": risk_factors,
        "summary": summary,
        "simple_recommendation": get_simple_recommendation(risk_scores["total_score"])
    }

def get_simple_recommendation(risk_score):
    """Provide a simple, actionable recommendation based on risk score."""
    if risk_score >= 60:
        return "Do not interact with this email. Report it as phishing and delete it."
    elif risk_score >= 40:
        return "Exercise caution with this email. Do not click any links or download attachments."
    elif risk_score >= 20:
        return "Proceed with caution. Verify the sender through other means if unsure."
    else:
        return "This email appears to be legitimate, but always be cautious with unexpected messages."

def calculate_confidence_score(risk_data, classification):
    """
    Calculate confidence score based on strength and alignment of evidence
    
    Args:
        risk_data (dict): Contains all risk assessments and scores
        classification (str): Final classification of the email
    
    Returns:
        tuple: (confidence_level, confidence_details)
    """
    # Extract relevant data
    technical_details = risk_data.get("technical_details", {})
    
    # Initialize evidence strength counters
    strong_evidence = 0
    contradicting_evidence = 0
    
    # 1. Evaluate URL-related evidence
    url_analysis = technical_details.get("detailed_analysis", {}).get("urls_analyzed", {})
    if url_analysis:
        malicious_urls = sum(1 for url in url_analysis.values() 
                           if url.get("status") == "Malicious")
        safe_urls = sum(1 for url in url_analysis.values() 
                      if url.get("status") == "Safe")
        
        if classification in ["suspicious", "phishing"]:
            strong_evidence += malicious_urls * 2  # Malicious URLs are strong evidence
            contradicting_evidence += safe_urls
        else:
            strong_evidence += safe_urls
            contradicting_evidence += malicious_urls * 2

    # 2. Evaluate content-based evidence
    content_analysis = technical_details.get("detailed_analysis", {}).get("content_analysis", {})
    if content_analysis:
        # Count high-risk indicators
        high_risk_indicators = len(content_analysis.get("request_indicators", [])) + \
                             len(content_analysis.get("threat_indicators", [])) + \
                             len(content_analysis.get("urgency_indicators", []))
        
        if classification in ["suspicious", "phishing"]:
            strong_evidence += high_risk_indicators
        elif high_risk_indicators > 0:
            contradicting_evidence += high_risk_indicators

    # 3. Evaluate domain evidence
    domain_analysis = technical_details.get("detailed_analysis", {}).get("sender_analysis", {})
    if domain_analysis:
        if classification in ["suspicious", "phishing"]:
            if domain_analysis.get("is_suspicious"):
                strong_evidence += 1
            if domain_analysis.get("is_free_email"):
                strong_evidence += 1
            if domain_analysis.get("whois_info", {}).get("is_new"):
                strong_evidence += 1
        else:
            if not domain_analysis.get("is_suspicious") and not domain_analysis.get("is_free_email"):
                strong_evidence += 1
            if domain_analysis.get("whois_info", {}).get("age_days", 0) > 365:
                strong_evidence += 1

    # 4. Calculate confidence score
    total_evidence = strong_evidence + contradicting_evidence
    if total_evidence == 0:
        confidence_score = 0.5  # Neutral when no evidence
    else:
        confidence_score = strong_evidence / total_evidence

    # 5. Determine confidence level
    if confidence_score >= 0.8:
        confidence_level = ConfidenceLevelEnum.MEDIUM
    elif confidence_score >= 0.6:
        confidence_level = ConfidenceLevelEnum.MEDIUM
    else:
        confidence_level = ConfidenceLevelEnum.LOW

    confidence_details = {
        "confidence_score": round(confidence_score * 100, 2),
        "supporting_evidence": strong_evidence,
        "contradicting_evidence": contradicting_evidence,
        "explanation": get_confidence_explanation(confidence_score, classification)
    }

    return confidence_level, confidence_details

def get_confidence_explanation(confidence_score, classification):
    """Generate human-readable explanation of confidence score"""
    if confidence_score >= 0.8:
        if classification in ["suspicious", "phishing"]:
            return "Multiple strong indicators of phishing with very little contradicting evidence"
        else:
            return "Multiple strong indicators of legitimacy with very little suspicious activity"
    elif confidence_score >= 0.6:
        return "Clear evidence supports the classification, but some factors are inconclusive"
    else:
        return "Mixed or weak evidence makes this classification less certain"
    

def calculate_combined_risk_score(model_score, risk_scores):
    """Calculate combined risk score using both model prediction and risk analysis."""
    # Convert model score to percentage (0-100)
    model_score_weighted = model_score * 100
    
    # Get risk analysis score (0-100)
    risk_analysis_score = risk_scores["total_score"]
    
    # Weight distribution
    MODEL_WEIGHT = 0.4
    RISK_WEIGHT = 0.6
    
    # Calculate combined score
    final_score = (model_score_weighted * MODEL_WEIGHT) + (risk_analysis_score * RISK_WEIGHT)
    
    # Calculate severity factors
    severity_factors = {
        "url_severity": risk_scores["url_risk"] / 40 * 100,
        "content_severity": risk_scores["content_risk"] / 40 * 100,
        "domain_severity": risk_scores["domain_risk"] / 20 * 100,
        "model_severity": model_score_weighted
    }
    
    # Determine classification and severity
    if final_score >= 60:
        classification = ThreatTypeEnum.PHISHING
        severity = ThreatSeverityEnum.HIGH
    elif final_score >= 50:
        classification = ThreatTypeEnum.SUSPICIOUS
        severity = ThreatSeverityEnum.MEDIUM_HIGH
    elif final_score >= 40:
        classification = ThreatTypeEnum.SUSPICIOUS
        severity = ThreatSeverityEnum.MEDIUM
    elif final_score >= 30:
        classification = ThreatTypeEnum.SUSPICIOUS
        severity = ThreatSeverityEnum.MEDIUM_LOW
    else:
        classification = ThreatTypeEnum.SAFE
        severity = ThreatSeverityEnum.LOW
    
    return {
        "final_score": round(final_score, 2),
        "classification": classification,
        "severity": severity,
        "score_breakdown": {
            "model_contribution": round(model_score_weighted * MODEL_WEIGHT, 2),
            "risk_contribution": round(risk_analysis_score * RISK_WEIGHT, 2),
            "severity_factors": {k: round(v, 2) for k, v in severity_factors.items()}
        }
    }


def determine_confidence_level(risk_data):
    """
    Determine the confidence level of the classification based on consistency of signals.
    
    Args:
        risk_data (dict): Contains severity factors and scores
        
    Returns:
        str: Confidence level (HIGH, MEDIUM, LOW)
    """
    severity_factors = risk_data["score_breakdown"]["severity_factors"]
    scores = list(severity_factors.values())
    
    # Calculate standard deviation of scores
    mean = sum(scores) / len(scores)
    variance = sum((x - mean) ** 2 for x in scores) / len(scores)
    std_dev = variance ** 0.5
    
    # Check consistency of signals
    if std_dev < 15:  # Signals are very consistent
        confidence = ConfidenceLevelEnum.HIGH
    elif std_dev < 30:  # Some variation in signals
        confidence = ConfidenceLevelEnum.MEDIUM
    else:  # High variation in signals
        confidence = ConfidenceLevelEnum.LOW
    
    return confidence

def detect_phishing(email: dict):
    """Main function to detect phishing emails with improved confidence scoring."""
    try:
        if not all(key in email for key in ["subject", "body", "sender", "recipient", "received_at"]):
            return {"error": "Missing required email fields"}
        
        # Prepare text for analysis
        email_text = f"{email['subject']} {email['body']}"
        truncated_text = truncate_text(email_text)
        
        # Get model prediction
        model_result = predictor(truncated_text)
        model_score = model_result[0]['score']
        
        # Perform analysis
        analysis_results = {
            "sender_analysis": analyze_sender_domain(email["sender"]),
            "content_analysis": analyze_text_content(email_text),
            "urls_analyzed": {
                url: check_url_reputation(url) 
                for url in extract_urls(email["body"])
            }
        }
        
        # Calculate risk scores
        risk_scores = calculate_risk_score(analysis_results)
        
        # Get combined risk assessment
        risk_assessment = calculate_combined_risk_score(model_score, risk_scores)
        
        # Get user-friendly explanations
        user_friendly_output = get_user_friendly_explanation(analysis_results, risk_scores)
        
        # Prepare complete result data
        result_data = {
            "classification": risk_assessment["classification"],
            "severity": risk_assessment["severity"],
            "final_score": risk_assessment["final_score"],
            "score_breakdown": risk_assessment["score_breakdown"],
            "summary": user_friendly_output["summary"],
            "risk_factors": user_friendly_output["risk_factors"],
            "recommendation": user_friendly_output["simple_recommendation"],
            "technical_details": {
                "risk_scores": risk_scores,
                "model_score": model_score,
                "text_length": {
                    "original_tokens": len(tokenizer.encode(email_text, add_special_tokens=True)),
                    "truncated_tokens": len(tokenizer.encode(truncated_text, add_special_tokens=True)),
                    "was_truncated": len(email_text) > len(truncated_text)
                },
                "detailed_analysis": analysis_results,
                "email_metadata": {
                    "sender": email["sender"],
                    "recipient": email["recipient"],
                    "received_at": email["received_at"]
                }
            }
        }
        
        # Calculate confidence using the new system
        confidence_level, confidence_details = calculate_confidence_score(result_data, risk_assessment["classification"])
        
        # Add confidence information to result
        result_data["confidence"] = confidence_level
        result_data["confidence_details"] = confidence_details
        
        return result_data
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}