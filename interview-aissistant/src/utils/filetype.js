
_getFileType(filename) {
  const extension = filename.split('.').pop().toLowerCase();
  
  // 更全面的类型判断
  const typeMap = {
    // 图片
    'jpg': 'images', 'jpeg': 'images', 'png': 'images',
    'gif': 'images', 'webp': 'images', 'svg': 'images',
    
    // 音频
    'mp3': 'audios', 'wav': 'audios', 'ogg': 'audios',
    'aac': 'audios', 'flac': 'audios',
    
    // 视频
    'mp4': 'videos', 'webm': 'videos', 'mov': 'videos',
    'avi': 'videos', 'mkv': 'videos',
    
    // 文档
    'pdf': 'documents', 'doc': 'documents', 'docx': 'documents',
    'xls': 'documents', 'xlsx': 'documents', 'ppt': 'documents',
    'pptx': 'documents', 'txt': 'documents'
  };
  
  return typeMap[extension] || 'documents';
}
export default {
    _getFileType
};