# 开发者文档

## 前言

> **不明确功能，就不可能明确方向。**

## 赛题要求

### 基本功能需求

1、场景覆盖：支持人工智能、大数据、物联网、智能系统等至少3个技术领域的典型岗位面试场景(如技术岗、运维测试岗、产品岗等);

2、多模态数据分析评测：整合语音(语言逻辑、情感语调)、视频(微表情、肢体语言)、文本(应答内容、简历)等多维度数据，构建动态量化评测体系;包含至少5项核心能力指标(如专业知识水平、技能匹配度、语言表达能力、逻辑思维能力、创新能力、应变抗压能力等);

3、智能反馈：支持生成可视化评测反馈报告，包含能力雷达图、关键问题定位及改进建议(如“回答缺乏STAR结构”、“眼神交流不足”);

### 实现条件

本赛题对开发环境、编程语言、数据库、编辑器、硬件平台等不限制，可借助开源工具完成，但要注意开源协议要求，确保智能体程序可正常运行;大模型要求使用讯飞星火大模型;智能体框架不限制框架，但智能体功能展示必须为中文;其他AI辅助工具使用科大讯飞相关工具。

<span style="color:red">也可以添加其他的小模型，使用其他的AI辅助工具</span>

## 推进

明确主要任务:提升分析性能.

完成单人模式,考虑导入数字人方便测试。

## 功能目标

1.主要功能:默认单人模式:先提交简历(支持纸质扫描成电子版),然后在完整一次面试过程中由ai自动根据简历内容生成问题。结束后生成报告，并且可以保存记录。如果未完成一次完整面试则不支持保存。报告的内容格式待定。
多人模式:待定
(附)未点击开始面试时，也可以映入镜头获取建议.

2.历史记录:按时间排序。对于每条记录，除了显示相关的时间节点，还显示总评(优秀、良好等).然后可以点击查看当时的录制视频、或者听音频、看当时提交的简历、更详细的报告(pdf/doc等)，可以在线预览也可以下载到本地。

3.社区功能。可以查看在线面试题目或者实时面试帖子，或者跳转相关网站，或者根据专业推荐相关网站或备战资源。

4.待定.

## 运行
- npm install
- npm run dev
- push前（如果安装了新的东西忘记使用--save）
- npm list,然后把输出结果和 package.json 一起提交给ai处理

## 接口  

#### POST 刷新令牌

POST /api/auth/refresh

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|username|query|string| 否 |none|
|email|query|string| 否 |none|
|password|query|string| 否 |none|

> 返回示例

> 200 Response

```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImp0aSI6Ind2amdNZElXMWVTZFV6TnZEMElJdUNlYUdrdjhINzc4SUYxUUhwRlhZaWZMVlBuNUNkYzIxSVJpc1VSY0huMjRzZ2xoUVdNV0s2cUR2eWJhVUhOeVhBIiwiZXhwIjoiMjAyNS0wNS0xMyAwNzowNDoyOCJ9.tPMW-o3GlXT4FXPlGzgFgwVrlNjSJNEVS2wphWWibqk",
    "token_type": "bearer",
    "expires_in": 300
  }
}
```


#### POST 注册

POST /api/auth/register

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|username|query|string| 是 |none|
|email|query|string| 否 |none|
|password|query|string| 是 |none|

> 返回示例

> 200 Response

```json
{
  "data": "注册成功"
}
```


#### POST 登录

POST /api/auth/login

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|username|query|string| 是 |none|
|email|query|string| 否 |none|
|password|query|string| 是 |none|

> 返回示例

> 200 Response

```json
{
  "data": {
    "id": 1,
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImp0aSI6ImtTV2VDMjVESThCd19QX0JUS0RoZEhnYzVQVUNOWk1oVWVFaGZqbGkxUldJZ21CMXc5NFFDQUl5Y3BKOWREckFsdC1saUJyd0FxMkRvVGJmeF9JaVJBIiwiZXhwIjoiMjAyNS0wNS0xMyAxMzoxMToxNiJ9.xGdqAgBpSEijWybPgUsReRT6LWRv60oCcp8iq1TW_48",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImp0aSI6ImtTV2VDMjVESThCd19QX0JUS0RoZEhnYzVQVUNOWk1oVWVFaGZqbGkxUldJZ21CMXc5NFFDQUl5Y3BKOWREckFsdC1saUJyd0FxMkRvVGJmeF9JaVJBIiwiZXhwIjoiMjAyNS0wNS0xMyAxMzoxMToxNiJ9.xGdqAgBpSEijWybPgUsReRT6LWRv60oCcp8iq1TW_48",
    "token_type": "bearer",
    "expired_in": 300000
  }
}
```


#### GET 获取用户信息

GET /api/user/get_info

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|username|query|string| 是 |none|

> 返回示例

> 200 Response

```json
{
  "data": {
    "id": 10,
    "username": "qwea",
    "email": "123@qq.com",
    "password": "qwe123456",
    "created_data": "2025-05-08",
    "preference": {
      "avatarSrc": "",
      "bio": ""
    }
  }
}
```

#### POST 文件上传

POST /api/upload

> Body 请求参数

```yaml
video: ""
audio: ""
image: ""

```

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 否 |none|
|» video|body|string(binary)¦null| 否 |none|
|» audio|body|string(binary)¦null| 否 |none|
|» image|body|string(binary)¦null| 否 |none|

> 返回示例

```json
{
  "code": 200,
  "message": "文件上传成功",
  "data": {
    "video_url": "",
    "audio_url": "",
    "image_url": ""
  }
}
```

```json
{
  "code": 400,
  "message": "没有要上传的文件",
  "data": ""
}
```

#### POST 下载文件

POST /api/download

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|url|query|array[string]| 否 |none|

> 返回示例

> 200 Response

```json
{
  "data": {}
}
```

#### POST 保存更新

POST /api/update

> Body 请求参数

```json
{
  "preference": {
    "avatarSrc": "",
    "bio": ""
  }
}
```

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|id|query|integer| 是 |ID 编号|
|username|query|string| 否 |none|
|email|query|string| 否 |none|
|body|body|object| 否 |none|

> 返回示例

> 200 Response

```json
{
  "message": "更新成功",
  "data": ""
}
```

#### GET 获取历史记录

GET /api/history

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|user_id|query|integer| 是 |用户ID|
|start_date|query|string| 否 |开始日期 (YYYY-MM-DD)|
|end_date|query|string| 否 |结束日期 (YYYY-MM-DD)|
|page|query|integer| 否 |页码，默认1|
|page_size|query|integer| 否 |每页记录数，默认10|

> 返回示例

```json
{
  "code": 200,
  "data": {
    "total": 25,
    "items": [
      {
        "id": 1,
        "user_id": 10,
        "created_at": "2024-03-20T10:30:00",
        "interview_type": "单人模式",
        "duration": 1800,
        "facial_score": 85,
        "voice_score": 90,
        "content_score": 88,
        "overall_score": 87.6,
        "suggestions": "表情自然，声音清晰，建议加强专业术语的使用",
        "video_url": "path/to/video",
        "audio_url": "path/to/audio"
      }
    ]
  }
}
```

#### DELETE 删除历史记录

DELETE /api/history/{record_id}

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|record_id|path|integer| 是 |记录ID|

> 返回示例

```json
{
  "code": 200,
  "message": "删除成功"
}
```

#### POST 保存面试记录

POST /api/history

> Body 请求参数

```json
{
  "user_id": 10,
  "interview_type": "单人模式",
  "duration": 1800,
  "facial_score": 85,
  "voice_score": 90,
  "content_score": 88,
  "suggestions": "表情自然，声音清晰，建议加强专业术语的使用",
  "video_url": "path/to/video",
  "audio_url": "path/to/audio"
}
```

###### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 是 |面试记录信息|

> 返回示例

```json
{
  "code": 200,
  "message": "保存成功",
  "data": {
    "id": 1
  }
}
```

