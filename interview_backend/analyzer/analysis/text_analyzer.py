import spacy
import numpy as np
from sentence_transformers import SentenceTransformer

class TextAnalyzer:
    def __init__(self):
        """初始化文本分析器"""
        try:
            # 加载语言模型
            self.nlp = spacy.load("zh_core_web_sm")
        except OSError:
            # 如果模型不存在，下载并加载
            spacy.cli.download("zh_core_web_sm")
            self.nlp = spacy.load("zh_core_web_sm")
            
        # 加载句子编码器
        try:
            self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            print(f"加载句子编码器失败: {str(e)}")
            self.encoder = None
        
    def analyze(self, text, resume_text=""):
        """分析文本内容"""
        try:
            if not text:
                return self._get_default_scores()
                
            # 处理文本
            doc = self.nlp(text)
            resume_doc = self.nlp(resume_text) if resume_text else None
            
            # 提取关键词
            keyword_count = len(self._extract_keywords(doc, resume_doc)) if resume_doc else 0
            
            # 计算连贯性
            content_coherence = self._calc_coherence(doc) if self.encoder else 0.5
            
            # 计算与简历的相似度
            resume_similarity = self._calc_resume_similarity(text, resume_text) if resume_text else 0.5
            
            return {
                "keyword_count": float(keyword_count),
                "content_coherence": float(content_coherence),
                "resume_similarity": float(resume_similarity)
            }
            
        except Exception as e:
            print(f"文本分析错误: {str(e)}")
            return self._get_default_scores()

    def _get_default_scores(self):
        """返回默认分数"""
        return {
            "keyword_count": 0.0,
            "content_coherence": 0.5,
            "resume_similarity": 0.5
        }

    def _extract_keywords(self, doc, resume_doc):
        """提取匹配的关键词"""
        if not doc or not resume_doc:
            return []
            
        try:
            # 获取非停用词的词根形式
            text_words = {token.lemma_ for token in doc 
                         if not token.is_stop and not token.is_punct}
            resume_words = {token.lemma_ for token in resume_doc 
                           if not token.is_stop and not token.is_punct}
            
            # 返回匹配的关键词列表
            return list(text_words & resume_words)
        except Exception as e:
            print(f"关键词提取错误: {str(e)}")
            return []
    
    def _calc_coherence(self, doc):
        """计算文本连贯性分数"""
        if not doc or not self.encoder:
            return 0.5
            
        try:
            sentences = list(doc.sents)
            if len(sentences) < 2:
                return 1.0
                
            # 计算相邻句子间的相似度
            embeddings = self.encoder.encode([sent.text for sent in sentences])
            similarities = []
            
            for i in range(len(embeddings)-1):
                similarity = self._cosine_sim(embeddings[i], embeddings[i+1])
                similarities.append(similarity)
                
            return float(np.mean(similarities))
        except Exception as e:
            print(f"连贯性计算错误: {str(e)}")
            return 0.5
    
    def _calc_resume_similarity(self, text, resume_text):
        """计算与简历的相似度"""
        if not text or not resume_text or not self.encoder:
            return 0.5
            
        try:
            # 编码文本
            text_embedding = self.encoder.encode([text])[0]
            resume_embedding = self.encoder.encode([resume_text])[0]
            
            # 计算余弦相似度
            return float(self._cosine_sim(text_embedding, resume_embedding))
        except Exception as e:
            print(f"简历相似度计算错误: {str(e)}")
            return 0.5
    
    def _cosine_sim(self, a, b):
        """计算余弦相似度"""
        try:
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except Exception as e:
            print(f"余弦相似度计算错误: {str(e)}")
            return 0.5 