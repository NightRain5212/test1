import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TextAnalyzer:
    def __init__(self):
        """初始化文本分析器"""
        self.vectorizer = TfidfVectorizer()
        
    async def analyze(self, text, resume_text=""):
        """分析文本内容"""
        try:
            # 分词
            text_words = list(jieba.cut(text))
            resume_words = list(jieba.cut(resume_text)) if resume_text else []
            
            # 计算关键词匹配度
            keyword_count = self._count_keywords(text_words, resume_words)
            
            # 计算内容连贯性
            content_coherence = self._calculate_coherence(text_words)
            
            # 计算与简历的相似度
            resume_similarity = self._calculate_similarity(text, resume_text) if resume_text else 0.0
            
            # 计算总分
            total = (
                keyword_count * 0.3 +
                content_coherence * 0.4 +
                resume_similarity * 0.3
            )
            
            return {
                "total": float(total),
                "details": {
                    "keyword_count": float(keyword_count),
                    "content_coherence": float(content_coherence),
                    "resume_similarity": float(resume_similarity)
                }
            }
            
        except Exception as e:
            print(f"文本分析错误: {str(e)}")
            return {
                "total": 0.0,
                "details": {
                    "keyword_count": 0.0,
                    "content_coherence": 0.0,
                    "resume_similarity": 0.0
                }
            }
    
    def _count_keywords(self, text_words, resume_words):
        """计算关键词匹配度"""
        try:
            if not resume_words:
                return 0.0
                
            # 统计简历中的关键词
            resume_keywords = set(resume_words)
            
            # 统计文本中匹配的关键词数量
            matched_keywords = sum(1 for word in text_words if word in resume_keywords)
            
            # 归一化到 0-1
            return min(matched_keywords / len(resume_keywords), 1.0)
            
        except Exception as e:
            print(f"关键词统计错误: {str(e)}")
            return 0.0
    
    def _calculate_coherence(self, words):
        """计算内容连贯性"""
        try:
            if not words:
                return 0.0
                
            # 计算词频
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 计算词频的方差
            frequencies = list(word_freq.values())
            variance = np.var(frequencies)
            
            # 归一化到 0-1
            return 1.0 / (1.0 + variance)
            
        except Exception as e:
            print(f"连贯性计算错误: {str(e)}")
            return 0.0
    
    def _calculate_similarity(self, text1, text2):
        """计算两段文本的相似度"""
        try:
            if not text1 or not text2:
                return 0.0
                
            # 使用 TF-IDF 向量化文本
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # 计算余弦相似度
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"相似度计算错误: {str(e)}")
            return 0.0 