# 大学生的面试助手  

## 功能  

1. 采集面部特征和声音信息  
2. 生成个性化信息表  
3. 根据数据提出智能化建议  
4. 提供数据可视化界面  
5. 提供经典面试题目  

## 目标

1. 帮助面试官一键搜集、整理、分析面试者信息  
2. 帮助大学生快速补充短板，提升面试技巧、缓解就业压力  

## 技术栈

1. vite+vue3  
2. 使用ant-design-vue进行UI设计  

## 特色

1. 不矫揉造作，力求简洁实用

## 运行

npm install  

npm run dev  

## 接口  

- /api/getuserinfo 给出用户信息，验证是否对应
- /api/refresh 返回新的refreshToken
- /api/getData 根据用户名或其他边缘信息获取全部具体数据
- /api/verify-code 请求发送验证码
- /api/register 发送用户信息，注册用户
- /api/saveData 保存用户数据
- ...
