import re
import numpy as np
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity

class AdvancedContentAnalyzer:
    def __init__(self):
        """
        Initialize NLP pipelines with explicit model selection and truncation.
        Higher thresholds and post-check logic reduce false positives for normal messages.
        """
        
        # Zero-Shot Intent Classification
        self.zero_shot = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            revision="main",
            truncation=True,
            max_length=512
        )
        
        # Sentiment Analysis
        self.sentiment = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            revision="main",
            truncation=True,
            max_length=512
        )
        
        # Emotion Classification
        self.emotion = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            revision="main",
            truncation=True,
            max_length=512
        )
        
        # Embedding Model (for Coherence)
        self.embedding_model = pipeline(
            "feature-extraction",
            model="sentence-transformers/all-MiniLM-L6-v2",
            revision="main",
            truncation=True,
            max_length=512
        )
        
        # Define the set of possible intent labels
        self.intent_labels = [
            "request personal information",
            "create urgency",
            "make threats",
            "offer rewards",
            "verify account",
            "business communication",
            "marketing",
            "general information"
        ]
        
        # Regex dictionaries to confirm suspicious keywords
        self._phishing_keywords = {
            # Typical PII or sensitive info keywords
            "request personal information": re.compile(
                r"(password|bank\s*account|credit\s*card|ssn|social\s*security|pin\s*number)",
                re.IGNORECASE
            ),
            # "Offer rewards" keywords (like prize, lottery, jackpot)
            "offer rewards": re.compile(
                r"(prize|reward|won|lottery|jackpot|giveaway)",
                re.IGNORECASE
            ),
            # "Make threats" keywords (like suspend, arrest, kill, blackmail)
            "make threats": re.compile(
                r"(suspend|terminate|arrest|punish|kill|die|terror|lawsuit|blackmail)",
                re.IGNORECASE
            )
        }
        
        # Higher thresholds to reduce false positives
        # If the model's score is below these, we ignore the label
        self.intent_thresholds = {
            "request personal information": 0.6,
            "create urgency": 0.6,
            "make threats": 0.7,
            "verify account": 0.5,
            "offer rewards": 0.6
        }
        
        # Weights for final risk scoring
        # Only if label passes threshold do we add the associated weight
        self.high_risk_intent_weights = {
            "request personal information": 0.8,
            "create urgency": 0.6,
            "make threats": 0.9,
            "verify account": 0.5,
            "offer rewards": 0.6
        }

    def analyze(self, text: str) -> dict:
        """Comprehensive content analysis using advanced NLP."""
        
        # 1. Zero-Shot Intent Classification
        intents = self.zero_shot(text, self.intent_labels, multi_label=True)
        
        # 2. Emotion & Sentiment
        emotions = self.emotion(text)
        sentiment = self.sentiment(text)
        
        # 3. Linguistic Analysis (Coherence, Formality)
        coherence_score = self._analyze_coherence(text)
        formality_score = self._analyze_formality(text)
        
        # 4. Combined Risk Assessment
        risk_signals = self._assess_risk_signals(intents, emotions[0], text, coherence_score)
        
        return {
            "intent_analysis": {
                "primary_intent": intents["labels"][0],
                "intent_confidence": round(intents["scores"][0], 3),
                "all_intents": dict(
                    zip(intents["labels"], [round(s, 3) for s in intents["scores"]])
                )
            },
            "emotional_signals": {
                "dominant_emotion": emotions[0]["label"],
                "emotion_confidence": round(emotions[0]["score"], 3),
                "sentiment": sentiment[0]["label"],
                "sentiment_confidence": round(sentiment[0]["score"], 3)
            },
            "linguistic_features": {
                "coherence": round(coherence_score, 3),
                "formality": round(formality_score, 3)
            },
            "risk_assessment": {
                "risk_score": round(risk_signals["risk_score"], 3),
                "manipulation_indicators": risk_signals["manipulation_indicators"],
                "risk_factors": risk_signals["risk_factors"]
            }
        }

    def _analyze_coherence(self, text: str) -> float:
        """
        Analyze semantic coherence by embedding sentences individually.
        This avoids shape mismatches and ensures each sentence is truncated properly if it's too long.
        """
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return 1.0
        
        sentence_embeddings = []
        for sent in sentences:
            output = self.embedding_model(sent)
            arr = np.array(output[0])  # shape: [seq_len, hidden_dim]
            arr_mean = arr.mean(axis=0)
            sentence_embeddings.append(arr_mean)
        
        embeddings = np.vstack(sentence_embeddings)  # [num_sentences, hidden_dim]
        
        # Average pairwise similarity between consecutive sentences
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
            similarities.append(sim)
        
        return float(np.mean(similarities))

    def _analyze_formality(self, text: str) -> float:
        """
        A simplistic formality measure:
         - 'formal' if words are somewhat longer
         - 'informal' if it contains casual words like hey, hi, hello, thanks
        """
        words = text.lower().split()
        total_words = len(words)
        if total_words == 0:
            return 1.0
        
        formal_indicators = sum(1 for w in words if len(w) > 6)
        informal_list = {"hey", "hi", "hello", "thanks"}
        informal_indicators = sum(1 for w in words if w in informal_list)
        
        score = (formal_indicators - informal_indicators) / total_words
        return max(0.0, min(1.0, score + 0.5))

    def _assess_risk_signals(self, intents, emotion, text: str, coherence: float) -> dict:
        """
        Assess overall risk based on:
          - High-risk intents (with higher thresholds + keyword checks)
          - Emotional manipulation (fear, anger)
          - Low coherence
        """
        risk_factors = []
        manipulation_indicators = []
        
        # Evaluate each predicted intent
        for label, score in zip(intents["labels"], intents["scores"]):
            # If not in threshold dict, skip
            if label not in self.intent_thresholds:
                continue
            
            # Only proceed if score >= threshold
            threshold = self.intent_thresholds[label]
            if score >= threshold:
                # (Optional) post-check for certain labels
                if label in self._phishing_keywords:
                    # If no suspicious keywords found in text, skip
                    if not self._phishing_keywords[label].search(text):
                        continue
                
                # If we reach here, it's a valid flagged intent
                risk_factors.append(f"High-risk intent: {label} ({score:.2f})")
                manipulation_indicators.append({
                    "type": "intent",
                    "detail": label,
                    "confidence": score
                })
        
        # Check emotional manipulation
        if emotion["label"] in ["fear", "anger"] and emotion["score"] > 0.5:
            risk_factors.append(f"Emotional manipulation: {emotion['label']}")
            manipulation_indicators.append({
                "type": "emotion",
                "detail": emotion["label"],
                "confidence": emotion["score"]
            })
        
        # Check coherence more leniently, e.g., < 0.3
        if coherence < 0.3:
            risk_factors.append("Low text coherence (potentially spammy or unclear)")
            manipulation_indicators.append({
                "type": "coherence",
                "detail": "inconsistent_text",
                "confidence": 1 - coherence
            })
        
        # Calculate combined risk score
        base_risk = 0.0
        for factor in risk_factors:
            for lbl, weight in self.high_risk_intent_weights.items():
                # If label text is in the factor string
                if lbl in factor.lower():
                    base_risk += weight
        
        # Emotion risk
        emotion_risk = 0.3 if (emotion["label"] in ["fear", "anger"] and emotion["score"] > 0.5) else 0
        
        # Coherence risk
        coherence_risk = 0.2 if coherence < 0.3 else 0
        
        # Combine and cap at 1.0
        risk_score = min(1.0, base_risk + emotion_risk + coherence_risk)
        
        return {
            "risk_score": risk_score,
            "manipulation_indicators": manipulation_indicators,
            "risk_factors": risk_factors
        }
