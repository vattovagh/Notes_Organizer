from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from typing import Dict, List, Tuple
import re

class TextClassifier:
    """
    AI-powered text classifier for categorizing notes into subjects
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        """
        Initialize text classifier
        
        Args:
            model_name: HuggingFace model name for zero-shot classification
        """
        self.model_name = model_name
        self.classifier = None
        self.tokenizer = None
        self.model = None
        
        # Define subject categories with their descriptions
        self.subjects = {
            "mathematics": "mathematical equations, formulas, calculations, algebra, calculus, geometry, trigonometry, statistics",
            "physics": "physical laws, mechanics, thermodynamics, electromagnetism, quantum physics, forces, energy, motion",
            "chemistry": "chemical reactions, molecular structures, periodic table, organic chemistry, inorganic chemistry, biochemistry",
            "biology": "living organisms, cells, genetics, evolution, anatomy, physiology, ecology, microbiology",
            "computer_science": "programming, algorithms, data structures, software development, computer systems, databases, networks",
            "history": "historical events, dates, people, civilizations, wars, political movements, cultural developments",
            "literature": "books, authors, poems, novels, literary analysis, writing, storytelling, language arts",
            "geography": "maps, countries, cities, physical features, climate, population, cultural geography",
            "economics": "economic theories, markets, supply and demand, financial concepts, business, trade, money",
            "psychology": "human behavior, mental processes, cognitive psychology, social psychology, neuroscience",
            "philosophy": "philosophical concepts, logic, ethics, metaphysics, epistemology, moral reasoning",
            "art": "artistic techniques, art history, visual arts, design, creativity, aesthetics, cultural expression",
            "music": "musical theory, instruments, composers, musical notation, rhythm, harmony, musical history",
            "medicine": "medical terminology, anatomy, diseases, treatments, healthcare, pharmacology, clinical practice",
            "engineering": "technical design, mechanical systems, electrical engineering, civil engineering, materials science",
            "astronomy": "celestial objects, space, planets, stars, galaxies, cosmology, astrophysics",
            "linguistics": "language structure, grammar, phonetics, syntax, semantics, language families, communication",
            "political_science": "government, politics, political systems, international relations, public policy, governance",
            "sociology": "social structures, human societies, social behavior, cultural patterns, social institutions",
            "environmental_science": "environmental issues, ecology, sustainability, climate change, natural resources, conservation"
        }
        
        self._load_model()
    
    def _load_model(self):
        """Load the classification model"""
        try:
            print("Loading classification model...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            # Fallback to CPU-only model
            try:
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model=self.model_name,
                    device=-1
                )
                print("Model loaded on CPU!")
            except Exception as e2:
                print(f"Failed to load model: {str(e2)}")
                self.classifier = None
    
    def classify_text(self, text: str, confidence_threshold: float = 0.3) -> Tuple[str, float]:
        """
        Classify text into a subject category
        
        Args:
            text: Text to classify
            confidence_threshold: Minimum confidence score to accept classification
            
        Returns:
            Tuple of (subject, confidence_score)
        """
        if not self.classifier or not text.strip():
            return "unknown", 0.0
        
        try:
            # Clean and prepare text
            cleaned_text = self._preprocess_text(text)
            
            if len(cleaned_text) < 10:  # Too short for reliable classification
                return "unknown", 0.0
            
            # Get candidate labels
            candidate_labels = list(self.subjects.keys())
            
            # Perform classification
            result = self.classifier(
                cleaned_text,
                candidate_labels,
                hypothesis_template="This text is about {}."
            )
            
            # Get best match
            best_label = result['labels'][0]
            best_score = result['scores'][0]
            
            # Check if confidence is above threshold
            if best_score >= confidence_threshold:
                return best_label, best_score
            else:
                return "unknown", best_score
                
        except Exception as e:
            print(f"Error classifying text: {str(e)}")
            return "unknown", 0.0
    
    def classify_multiple_texts(self, texts: List[str], confidence_threshold: float = 0.3) -> List[Tuple[str, str, float]]:
        """
        Classify multiple texts
        
        Args:
            texts: List of texts to classify
            confidence_threshold: Minimum confidence score
            
        Returns:
            List of tuples (text, subject, confidence_score)
        """
        results = []
        
        for text in texts:
            subject, confidence = self.classify_text(text, confidence_threshold)
            results.append((text, subject, confidence))
        
        return results
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for classification
        
        Args:
            text: Raw text
            
        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', ' ', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove very short words (likely OCR artifacts)
        words = text.split()
        words = [word for word in words if len(word) > 2]
        
        return ' '.join(words)
    
    def get_subject_description(self, subject: str) -> str:
        """
        Get description for a subject
        
        Args:
            subject: Subject name
            
        Returns:
            Subject description
        """
        return self.subjects.get(subject, "Unknown subject")
    
    def get_all_subjects(self) -> Dict[str, str]:
        """
        Get all available subjects and their descriptions
        
        Returns:
            Dictionary of subjects and descriptions
        """
        return self.subjects.copy()
    
    def add_custom_subject(self, subject_name: str, description: str):
        """
        Add a custom subject category
        
        Args:
            subject_name: Name of the subject
            description: Description of what the subject covers
        """
        self.subjects[subject_name.lower()] = description
    
    def get_classification_confidence(self, text: str, subject: str) -> float:
        """
        Get confidence score for a specific subject classification
        
        Args:
            text: Text to classify
            subject: Subject to check confidence for
            
        Returns:
            Confidence score (0-1)
        """
        if not self.classifier or subject not in self.subjects:
            return 0.0
        
        try:
            cleaned_text = self._preprocess_text(text)
            
            if len(cleaned_text) < 10:
                return 0.0
            
            result = self.classifier(
                cleaned_text,
                [subject],
                hypothesis_template="This text is about {}."
            )
            
            return result['scores'][0]
            
        except Exception as e:
            print(f"Error getting confidence: {str(e)}")
            return 0.0 