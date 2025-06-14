# 开发者文档

## 推进

核心分为两大模块：图像检测，音频检测。

后端提升分析性能,维护数据库

前端完善实时交互相关功能

## 运行# 开发者文档

## 推进

核心分为两大模块：图像检测，音频检测。

后端提升分析性能,维护数据库

前端完善实时交互相关功能

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


## 功能目标

1.主体有开始面试，分为单人模式和双人模式。单人模式下，可以选择是否开启录音或录像，是否开启ai自动提问。多人模式下，由一人充当面试官，可以借助内置ai或者记录生成问题来提问，并且可以随时对记录的信息增改，实时观看可视化结果和分析结果以及ai建议，另一人选择坐在或站在电脑后，正对屏幕，回答问题，系统可以自动分辩说话者。

2.社区功能。可以查看在线面试题目或者实时面试帖子，或者跳转相关网站，或者根据专业推荐相关网站或备战资源。

3.可以发布面试经验贴，查看他人帖子。

4.可以导入校园社区，区分学长校友，咨询获得建议。


- npm install
- npm run dev
- push前（如果安装了新的东西忘记使用--save）
- npm list,然后把输出结果和 package.json 一起提交给ai处理

## 接口  

- /api/auth/refresh  发送refresh_token获取新的access_token
- /api/user/get_info  根据提供的信息查询用户信息,这里现在只给username  
- /api/auth/register 给出用户名和密码等，注册用户，返回字段不含data则用户已经注册;默认用户还要登录
- /api/auth/login  给出用户名和密码，登录用户，返回新的令牌

## 功能目标

1.主体有开始面试，分为单人模式和双人模式。单人模式下，可以选择是否开启录音或录像，是否开启ai自动提问。多人模式下，由一人充当面试官，可以借助内置ai或者记录生成问题来提问，并且可以随时对记录的信息增改，实时观看可视化结果和分析结果以及ai建议，另一人选择坐在或站在电脑后，正对屏幕，回答问题，系统可以自动分辩说话者。

2.社区功能。可以查看在线面试题目或者实时面试帖子，或者跳转相关网站，或者根据专业推荐相关网站或备战资源。

3.可以发布面试经验贴，查看他人帖子。

4.可以导入校园社区，区分学长校友，咨询获得建议。

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

