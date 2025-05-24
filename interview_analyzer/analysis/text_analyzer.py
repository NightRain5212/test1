import spacy
import numpy as np
from sentence_transformers import SentenceTransformer

class TextAnalyzer:
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        """
        初始化文本分析器
        model_name: sentence-transformers模型名称
        """
        self.nlp = spacy.load("zh_core_web_sm")
        self.encoder = SentenceTransformer(model_name)
        
    def analyze(self, text, resume_text):
        """分析面试文本与简历的相关性"""
        # 文本预处理
        doc = self.nlp(text)
        resume_doc = self.nlp(resume_text)
        
        # 生成文本嵌入
        text_embedding = self.encoder.encode(text)
        resume_embedding = self.encoder.encode(resume_text)
        
        # 计算各项指标
        keyword_matches = self._extract_keywords(doc, resume_doc)
        coherence_score = self._calc_coherence(doc)
        similarity_score = self._cosine_sim(text_embedding, resume_embedding)
        
        return {
            "keyword_matches": keyword_matches,  # 关键词匹配列表
            "keyword_count": len(keyword_matches),  # 关键词匹配数量
            "content_coherence": coherence_score,  # 内容连贯性分数
            "resume_similarity": similarity_score,  # 与简历的相似度
            "sentence_count": len(list(doc.sents)),  # 句子数量
            "word_count": len([token for token in doc if not token.is_punct])  # 词数
        }
    
    def _extract_keywords(self, doc, resume_doc):
        """提取匹配的关键词"""
        # 获取非停用词的词根形式
        text_words = {token.lemma_ for token in doc 
                     if not token.is_stop and not token.is_punct}
        resume_words = {token.lemma_ for token in resume_doc 
                       if not token.is_stop and not token.is_punct}
        
        # 返回匹配的关键词列表
        return list(text_words & resume_words)
    
    def _calc_coherence(self, doc):
        """计算文本连贯性分数"""
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
    
    def _cosine_sim(self, a, b):
        """计算余弦相似度"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))) 