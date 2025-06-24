<template>
  <div class="resume-editor-container">
    <!-- 双栏布局 -->
    <div class="editor-column">
      <!-- 基本信息 -->
      <a-card title="基本信息" size="small" class="section-card">
        <a-form :model="formData" layout="vertical">
          <div class="basic-info-grid">
            <a-form-item label="姓名" class="grid-item">
              <a-input v-model:value="formData.name" placeholder="请输入姓名" />
            </a-form-item>
            <a-form-item label="年龄" class="grid-item">
              <a-input-number v-model:value="formData.age" :min="16" :max="70" />
            </a-form-item>
            <a-form-item label="性别" class="grid-item">
              <a-select v-model:value="formData.gender" placeholder="请选择">
                <a-select-option value="male">男</a-select-option>
                <a-select-option value="female">女</a-select-option>
                <a-select-option value="other">其他</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="联系方式" class="grid-item">
              <a-input v-model:value="formData.phone" placeholder="手机/邮箱" />
            </a-form-item>
          </div>
          <a-form-item label="照片上传">
            <a-upload v-model:file-list="fileList" list-type="picture-card" :before-upload="beforeUpload"
              @preview="handlePreview">
              <div v-if="fileList.length < 1">
                <plus-outlined />
                <div style="margin-top: 8px">上传照片</div>
              </div>
            </a-upload>
          </a-form-item>
        </a-form>
      </a-card>

      <!-- 学历背景 -->
      <a-card title="学历背景" size="small" class="section-card">
        <a-form-item v-for="(edu, index) in formData.education" :key="index">
          <div class="edu-item">
            <a-input v-model:value="edu.school" placeholder="学校名称" style="width: 40%" />
            <a-input v-model:value="edu.major" placeholder="专业" style="width: 30%; margin: 0 8px" />
            <a-input-number v-model:value="edu.gpa" :min="0" :max="4" :step="0.1" placeholder="GPA" />
            <a-button type="link" danger @click="removeEdu(index)" style="margin-left: 8px">
              <delete-outlined />
            </a-button>
          </div>
        </a-form-item>
        <a-button type="dashed" @click="addEdu">
          <plus-outlined /> 添加学历
        </a-button>
      </a-card>

      <!-- 个人成果 -->
      <a-card title="个人成果" size="small" class="section-card">
        <a-tabs>
          <a-tab-pane key="awards" tab="获奖情况">
            <draggable v-model="formData.awards" item-key="id">
              <template #item="{ element, index }">
                <div class="achievement-item">
                  <a-input v-model:value="element.text" placeholder="例: 2023年全国大学生数学竞赛一等奖" />
                  <a-button type="link" danger @click="removeAward(index)">
                    <delete-outlined />
                  </a-button>
                </div>
              </template>
            </draggable>
            <a-button type="dashed" @click="addAward">
              <plus-outlined /> 添加获奖
            </a-button>
          </a-tab-pane>
          <a-tab-pane key="research" tab="科研成果">
            <draggable v-model="formData.research" item-key="id">
              <template #item="{ element, index }">
                <div class="achievement-item">
                  <a-input v-model:value="element.text" placeholder="例: 发表SCI论文《...》于《Nature》期刊" />
                  <a-button type="link" danger @click="removeResearch(index)">
                    <delete-outlined />
                  </a-button>
                </div>
              </template>
            </draggable>
            <a-button type="dashed" @click="addResearch">
              <plus-outlined /> 添加成果
            </a-button>
          </a-tab-pane>
        </a-tabs>
      </a-card>

      <!-- 个人经历 -->
      <a-card title="个人经历" size="small" class="section-card">
        <editor-content :editor="experienceEditor" class="editor-content" />
      </a-card>

      <!-- 自我介绍 -->
      <a-card title="自我介绍/职业期望" size="small" class="section-card">
        <editor-content :editor="introductionEditor" class="editor-content" />
      </a-card>
    </div>

    <!-- 预览区 -->
    <div class="preview-column">
      <div class="resume-preview">
        <!-- 基本信息头部 -->
        <div class="preview-header">
          <div class="basic-info-left">
            <h1 class="name">{{ formData.name || '姓名' }}</h1>
            <div class="basic-info-details">
              <div v-if="formData.age" class="info-item">年龄: {{ formData.age }}岁</div>
              <div v-if="formData.gender" class="info-item">性别: {{ genderMap[formData.gender] }}</div>
              <div v-if="formData.phone" class="info-item">电话: {{ formData.phone }}</div>
            </div>
          </div>
          <div v-if="fileList.length > 0" class="photo-preview">
            <img :src="fileList[0].thumbUrl" alt="个人照片" />
          </div>
        </div>

        <!-- 教育背景 -->
        <div class="preview-section">
          <h2 class="section-title">教育背景</h2>
          <ul class="edu-list">
            <li v-for="(edu, index) in formData.education" :key="index">
              <div class="edu-item">
                <span class="edu-school">{{ edu.school || '学校名称' }}</span>
                <span class="edu-major">{{ edu.major || '专业' }}</span>
                <span class="edu-gpa" v-if="edu.gpa">GPA: {{ edu.gpa }}</span>
              </div>
            </li>
          </ul>
        </div>

        <!-- 个人成果 -->
        <div class="preview-section">
          <h2 class="section-title">个人成果</h2>
          <div class="achievements">
            <div class="achievement-type">
              <h3 class="achievement-title">获奖情况</h3>
              <ul>
                <li v-for="(award, index) in formData.awards" :key="'award' + index">
                  {{ award.text || '获奖内容' }}
                </li>
              </ul>
            </div>
            <div class="achievement-type">
              <h3 class="achievement-title">科研成果</h3>
              <ul>
                <li v-for="(research, index) in formData.research" :key="'research' + index">
                  {{ research.text || '科研成果' }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 经历和自我介绍 -->
        <div class="preview-section">
          <h2 class="section-title">个人经历</h2>
          <div class="content-text" v-html="experienceHtml"></div>
        </div>

        <div class="preview-section">
          <h2 class="section-title">自我介绍</h2>
          <div class="content-text" v-html="introductionHtml"></div>
        </div>
      </div>
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
import { ref, reactive, onMounted, onBeforeUnmount, computed } from 'vue';
import { Editor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { PlusOutlined, DeleteOutlined, FilePdfOutlined, FileWordOutlined, SaveOutlined } from '@ant-design/icons-vue';
import {message}from 'ant-design-vue';
import draggable from 'vuedraggable';
import { jsPDF } from 'jspdf';
import { Packer } from 'docx';
import { Document, Paragraph, TextRun } from 'docx';
import { NButton } from 'naive-ui';
// 表单数据
const formData = reactive({
  name: '',
  age: null,
  gender: undefined,
  phone: '',
  education: [
    { school: '', major: '', gpa: null }
  ],
  awards: [],
  research: []
});

const genderMap = {
  male: '男',
  female: '女',
  other: '其他'
};

// 照片上传
const fileList = ref([]);
const beforeUpload = file => {
  fileList.value = [file];
  return false;
};

// 学历管理
const addEdu = () => {
  formData.education.push({ school: '', major: '', gpa: null });
};
const removeEdu = index => {
  formData.education.splice(index, 1);
};

// 成果管理
const addAward = () => {
  formData.awards.push({ id: Date.now(), text: '' });
};
const removeAward = index => {
  formData.awards.splice(index, 1);
};
const addResearch = () => {
  formData.research.push({ id: Date.now(), text: '' });
};
const removeResearch = index => {
  formData.research.splice(index, 1);
};

// 编辑器实例
const experienceEditor = ref(null);
const experienceHtml = ref('');
const introductionEditor = ref(null);
const introductionHtml = ref('');

onMounted(() => {
  experienceEditor.value = new Editor({
    content: '<p>请详细描述您的工作/项目经历...</p>',
    extensions: [StarterKit],
    onUpdate: ({ editor }) => {
      experienceHtml.value = editor.getHTML();
    }
  });

  introductionEditor.value = new Editor({
    content: '<p>请描述您的个人优势、职业目标等...</p>',
    extensions: [StarterKit],
    onUpdate: ({ editor }) => {
      introductionHtml.value = editor.getHTML();
    }
  });
});

onBeforeUnmount(() => {
  experienceEditor.value?.destroy();
  introductionEditor.value?.destroy();
});

// 导出PDF功能
const exportPDF = () => {
  const resumeContent = document.querySelector('.resume-preview');
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm'
  });

  // 使用html2canvas或其他库来捕获DOM元素
  // 这里简化处理，实际项目中你可能需要html2canvas或dom-to-image
  // 以下是基本实现，可能需要调整
  
  // 临时解决方案：将内容转换为图片
  // 注意：实际项目中应安装html2canvas并导入
  // import html2canvas from 'html2canvas';
  
  // 模拟html2canvas功能
  /*
  html2canvas(resumeContent).then(canvas => {
    const imgData = canvas.toDataURL('image/png');
    const imgWidth = 210; // A4 width in mm
    const pageHeight = 295; // A4 height in mm
    const imgHeight = canvas.height * imgWidth / canvas.width;
    let heightLeft = imgHeight;
    let position = 0;
    
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
    
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }
    
    pdf.save('resume.pdf');
  });
  */
  
  // 简单文本导出作为替代方案
  let yPos = 10;
  
  // 添加姓名
  pdf.setFontSize(20);
  pdf.text(formData.name || '姓名', 105, yPos, { align: 'center' });
  yPos += 10;
  
  // 添加基本信息
  pdf.setFontSize(12);
  let basicInfo = [];
  if (formData.age) basicInfo.push(`年龄: ${formData.age}岁`);
  if (formData.gender) basicInfo.push(`性别: ${genderMap[formData.gender]}`);
  if (formData.phone) basicInfo.push(`电话: ${formData.phone}`);
  
  pdf.text(basicInfo.join(' | '), 105, yPos, { align: 'center' });
  yPos += 10;
  
  // 添加教育背景
  pdf.setFontSize(14);
  pdf.text('教育背景', 15, yPos);
  yPos += 8;
  pdf.setFontSize(12);
  
  formData.education.forEach(edu => {
    let eduText = `${edu.school || '学校名称'} | ${edu.major || '专业'}`;
    if (edu.gpa) eduText += ` | GPA: ${edu.gpa}`;
    pdf.text(eduText, 20, yPos);
    yPos += 7;
  });
  yPos += 5;
  
  // 添加个人成果
  pdf.setFontSize(14);
  pdf.text('个人成果', 15, yPos);
  yPos += 8;
  pdf.setFontSize(12);
  
  // 获奖情况
  pdf.text('获奖情况:', 20, yPos);
  yPos += 7;
  formData.awards.forEach(award => {
    pdf.text(`- ${award.text || '获奖内容'}`, 25, yPos);
    yPos += 7;
  });
  yPos += 5;
  
  // 科研成果
  pdf.text('科研成果:', 20, yPos);
  yPos += 7;
  formData.research.forEach(research => {
    pdf.text(`- ${research.text || '科研成果'}`, 25, yPos);
    yPos += 7;
  });
  yPos += 5;
  
  // 个人经历
  pdf.setFontSize(14);
  pdf.text('个人经历', 15, yPos);
  yPos += 8;
  pdf.setFontSize(12);
  const experienceLines = experienceText.value.split('\n');
  experienceLines.forEach(line => {
    if (yPos > 280) {
      pdf.addPage();
      yPos = 20;
    }
    pdf.text(line, 20, yPos);
    yPos += 7;
  });
  yPos += 5;
  
  // 自我介绍
  pdf.setFontSize(14);
  pdf.text('自我介绍', 15, yPos);
  yPos += 8;
  pdf.setFontSize(12);
  const introLines = introductionText.value.split('\n');
  introLines.forEach(line => {
    if (yPos > 280) {
      pdf.addPage();
      yPos = 20;
    }
    pdf.text(line, 20, yPos);
    yPos += 7;
  });
  
  pdf.save('resume.pdf');
};

// 导出Word功能
const exportDOCX = async () => {
  const doc = new Document({
    sections: [{
      properties: {},
      children: [
        // 标题
        new Paragraph({
          text: formData.name || '姓名',
          heading: "Heading1",
          alignment: "center"
        }),
        
        // 基本信息
        new Paragraph({
          children: [
            new TextRun({
              text: [
                formData.age ? `年龄: ${formData.age}岁` : '',
                formData.gender ? `性别: ${genderMap[formData.gender]}` : '',
                formData.phone ? `电话: ${formData.phone}` : ''
              ].filter(Boolean).join(' | '),
              size: 24
            })
          ],
          alignment: "center"
        }),
        
        // 教育背景
        new Paragraph({
          text: "教育背景",
          heading: "Heading2"
        }),
        ...formData.education.flatMap(edu => [
          new Paragraph({
            children: [
              new TextRun({
                text: `${edu.school || '学校名称'} | ${edu.major || '专业'}`,
                bold: true
              }),
              ...(edu.gpa ? [new TextRun({
                text: ` | GPA: ${edu.gpa}`,
                bold: false
              })] : [])
            ],
            indent: { left: 400 }
          })
        ]),
        
        // 获奖情况
        new Paragraph({
          text: "获奖情况",
          heading: "Heading2"
        }),
        ...formData.awards.flatMap(award => [
          new Paragraph({
            text: `• ${award.text || '获奖内容'}`,
            indent: { left: 400 }
          })
        ]),
        
        // 科研成果
        new Paragraph({
          text: "科研成果",
          heading: "Heading2"
        }),
        ...formData.research.flatMap(research => [
          new Paragraph({
            text: `• ${research.text || '科研成果'}`,
            indent: { left: 400 }
          })
        ]),
        
        // 个人经历
        new Paragraph({
          text: "个人经历",
          heading: "Heading2"
        }),
        new Paragraph({
          text: experienceText.value,
          indent: { left: 400 }
        }),
        
        // 自我介绍
        new Paragraph({
          text: "自我介绍",
          heading: "Heading2"
        }),
        new Paragraph({
          text: introductionText.value,
          indent: { left: 400 }
        })
      ]
    }]
  });
  
  const blob = await Packer.toBlob(doc);
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'resume.docx';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 计算纯文本内容
const experienceText = computed(() => {
  return formData.experience ? formData.experience.replace(/<[^>]*>/g, '\n') : '';
});

const introductionText = computed(() => {
  return formData.introduction ? formData.introduction.replace(/<[^>]*>/g, '\n') : '';
});

// 提交数据
const emit = defineEmits(['submit']);
const submit = () => {
  message.info('提交成功！');
  return;
  emit('submit', {
    ...formData,
    experience: experienceHtml.value,
    introduction: introductionHtml.value,
    photo: fileList.value[0]?.thumbUrl
  });
};
</script>

<style lang="scss" scoped>
.resume-editor-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 24px;
  padding: 24px;
  width: 90%;
  max-width: 1200px;
  height: 80vh;
  max-height: 800px;
  margin: 0 auto;
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  overflow: hidden;
  z-index: 1000;

  /* 编辑器列 */
  .editor-column {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    padding-right: 12px;

    /* 卡片样式 */
    .section-card {
      margin-bottom: 16px;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);

      /* 基本信息网格 */
      .basic-info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-bottom: 12px;

        .grid-item {
          margin-bottom: 0;
        }
      }

      /* 教育经历项 */
      .edu-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        :deep(.ant-input-number) {
          width: 80px;
        }
      }

      /* 成果项 */
      .achievement-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
      }

      /* 编辑器内容区 */
      .editor-content {
        min-height: 200px;
        border: 1px solid #d9d9d9;
        border-radius: 4px;
        padding: 12px;
        background: #fff;
      }

      /* 添加按钮 */
      .ant-btn-dashed {
        width: 100%;
        margin-top: 8px;
      }
    }
  }

  /* 预览列 */
  .preview-column {
    flex: 1;
    min-width: 0;
    background: #f9f9f9;
    border-radius: 8px;
    overflow-y: auto;
    padding: 20px;

    .resume-preview {
      background: white;
      padding: 30px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
      font-family: 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.5;
      color: #333;

      /* 头部信息 */
      .preview-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
        border-bottom: 1px solid #eee;
        padding-bottom: 20px;

        .basic-info-left {
          flex: 1;

          .name {
            font-size: 22px;
            font-weight: 600;
            margin: 0 0 10px 0;
            color: #222;
          }

          .basic-info-details {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;

            .info-item {
              font-size: 14px;
              color: #555;
            }
          }
        }

        .photo-preview {
          width: 100px;
          height: 120px;
          border: 1px solid #eee;
          overflow: hidden;

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }
      }

      /* 各部分通用样式 */
      .preview-section {
        margin-bottom: 20px;

        .section-title {
          font-size: 16px;
          font-weight: 600;
          color: #333;
          border-bottom: 1px solid #eee;
          padding-bottom: 6px;
          margin: 20px 0 12px 0;
        }
      }

      /* 教育背景 */
      .edu-list {
        list-style: none;
        padding: 0;
        margin: 0;

        li {
          margin-bottom: 10px;

          .edu-item {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;

            .edu-school {
              font-weight: 500;
            }

            .edu-major {
              color: #555;
            }

            .edu-gpa {
              font-size: 13px;
              color: #777;
            }
          }
        }
      }

      /* 个人成果 */
      .achievements {
        display: flex;
        gap: 30px;

        .achievement-type {
          flex: 1;

          .achievement-title {
            font-size: 14px;
            font-weight: 500;
            margin: 10px 0 8px 0;
            color: #444;
          }

          ul {
            list-style-type: disc;
            padding-left: 20px;
            margin: 0;
            font-size: 13px;
            color: #555;

            li {
              margin-bottom: 6px;
            }
          }
        }
      }

      /* 内容文本 */
      .content-text {
        font-size: 13px;
        line-height: 1.6;
        color: #444;

        :deep(p) {
          margin: 0 0 10px 0;
        }
      }
    }
  }

  /* 操作按钮 */
  .editor-actions {
    position: fixed;
    right: 32px;
    bottom: 32px;
    display: flex;
    gap: 12px;
    z-index: 2000;

    button {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      }
    }
  }
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>