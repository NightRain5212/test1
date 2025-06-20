<template>
  <div class="resume-editor-container">
    <!-- 编辑器与预览双栏布局 -->
    <div class="editor-column">
      <!-- 基本信息表单 -->
      <a-form :model="formData" layout="vertical">
        <a-form-item label="姓名">
          <a-input v-model:value="formData.name" />
        </a-form-item>
        <a-form-item label="联系方式">
          <a-input v-model:value="formData.phone" />
        </a-form-item>
      </a-form>

      <!-- Tiptap 富文本编辑器 -->
      <div class="editor-toolbar">
        <!-- 所有编辑器按钮添加 v-if="isEditorReady" -->
        <button 
          v-if="isEditorReady"
          @click="editor.chain().focus().toggleBold().run()"
          :class="{ 'is-active': editor.isActive('bold') }"
        >
          <bold-outlined />
        </button>
        <button 
          v-if="isEditorReady"
          @click="editor.chain().focus().toggleItalic().run()"
          :class="{ 'is-active': editor.isActive('italic') }"
        >
          <italic-outlined />
        </button>
      </div>
      
      <editor-content :editor="editor" class="editor-content" />
    </div>

    <!-- 实时预览 -->
    <div class="preview-column">
      <h3>{{ formData.name || '姓名' }}</h3>
      <p>{{ formData.phone || '联系电话' }}</p>
      <div v-html="htmlPreview" class="preview-content"></div>
    </div>

    <!-- 操作按钮 -->
    <div class="editor-actions">
      <a-button @click="exportDOCX">
        <file-word-outlined /> 导出Word
      </a-button>
      <a-button @click="exportPDF">
        <file-pdf-outlined /> 导出PDF
      </a-button>
      <a-button type="primary" @click="submit">
        <save-outlined /> 保存并使用
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Editor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { BoldOutlined, ItalicOutlined, SaveOutlined, FilePdfOutlined, FileWordOutlined } from '@ant-design/icons-vue';
import { jsPDF } from 'jspdf';
import { Packer } from 'docx';
import { Document, Paragraph, TextRun } from 'docx';

// 编辑器实例
const editor = ref(null);
const htmlPreview = ref('');

// 表单数据
const formData = ref({
  name: '',
  phone: '',
  content: ''
});

// 初始化编辑器
onMounted(() => {
  editor.value = new Editor({
    content: '<p>开始编辑您的简历...</p>',
    extensions: [StarterKit],
    onUpdate: ({ editor }) => {
      htmlPreview.value = editor.getHTML();
      formData.value.content = editor.getHTML();
    }
  });
});

// 清理编辑器
onBeforeUnmount(() => {
  editor.value?.destroy();
});

// 导出为PDF
const exportPDF = async () => {
  const doc = new jsPDF();
  const content = `
    姓名: ${formData.value.name}
    电话: ${formData.value.phone}
    ${editor.value.getText()}
  `;
  doc.text(content, 10, 10);
  doc.save('resume.pdf');
};

// 导出为DOCX
const exportDOCX = async () => {
  const doc = new Document({
    sections: [{
      properties: {},
      children: [
        new Paragraph({
          children: [
            new TextRun({
              text: `姓名: ${formData.value.name}`,
              bold: true
            })
          ]
        }),
        new Paragraph({
          children: [
            new TextRun(`电话: ${formData.value.phone}`)
          ]
        }),
        new Paragraph({
          children: [
            new TextRun(editor.value.getText())
          ]
        })
      ]
    }]
  });

  Packer.toBlob(doc).then(blob => {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'resume.docx';
    link.click();
  });
};

// 提交数据
const emit = defineEmits(['submit']);
const submit = () => {
  emit('submit', {
    ...formData.value,
    html: htmlPreview.value,
    text: editor.value.getText()
  });
};
</script>

<style scoped>
.resume-editor-container {
  display: flex;
  height: 100%;
  gap: 20px;
}

.editor-column, .preview-column {
  flex: 1;
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  overflow-y: auto;
}

.editor-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 12px;
}

.editor-toolbar button {
  padding: 4px 8px;
  background: none;
  border: 1px solid #d9d9d9;
  border-radius: 2px;
  cursor: pointer;
}

.editor-toolbar button.is-active {
  background: #e6f7ff;
  border-color: #1890ff;
}

.editor-content {
  min-height: 300px;
  padding: 8px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
}

.preview-content {
  margin-top: 20px;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}
</style>