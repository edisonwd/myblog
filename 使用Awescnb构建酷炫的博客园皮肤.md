# 使用Awescnb构建酷炫的博客园皮肤

# 一. 概述

>  基于 vite 和 webpack 5，构建、安装、切换博客园皮肤
>
>  源码地址：https://gitee.com/guangzan/awescnb

经常浏览博客园，看到别人的博客非常酷炫，所以也想定义一个酷炫的页面，但是发现自己的前端 css 水平太差，只会修改博客园的字体大小和颜色，百度了一下相关的文档，找到了 `awescnb` 这个开源仓库，能够满足我的需求，接下来我将记录一下自己使用  `awescnb` 构建博客园皮肤的过程，更多详细的配置可以查看文章后面的参考文档。

下面是我使用  `awescnb` 构建的博客园：

![image-20211203184959078](https://gitee.com/peterwd/pic-oss/raw/master/image/202112031849416.png)

# 二. 使用Awescnb安装博客园皮肤

1. 打开你的博客首页 -> 管理 -> 设置

![image-20211203191317055](https://gitee.com/peterwd/pic-oss/raw/master/image/202112031913199.png)



2. 设置博客皮肤为 `Custom` ，渲染引擎选择 `highlight.js`，取消勾选显示行号，主题样式选择默认的 `cnblogs`

![image-20211203192246122](https://gitee.com/peterwd/pic-oss/raw/master/image/202112031922237.png)



3. 复制如下代码粘贴到【页面定制 CSS】并禁用默认 CSS 样式

```css
#loading{bottom:0;left:0;position:fixed;right:0;top:0;z-index:9999;background-color:#f4f5f5;pointer-events:none;}.loader-inner{will-change:transform;width:40px;height:40px;position:absolute;top:50%;left:50%;margin:-20px 0 0 -20px;background-color:#3742fa;border-radius:50%;animation:scaleout 0.6s infinite ease-in-out forwards;text-indent:-99999px;z-index:999991;}@keyframes scaleout{0%{transform:scale(0);opacity:0;}40%{opacity:1;}100%{transform:scale(1);opacity:0;}}
```
![image-20211203192651059](https://gitee.com/peterwd/pic-oss/raw/master/image/202112031926168.png)

4. 复制如下代码粘贴到【页首 HTML】

```html
<div id="loading"><div class="loader-inner"></div></div>
```

![image-20211203192738007](https://gitee.com/peterwd/pic-oss/raw/master/image/202112031927107.png)



5. 复制如下代码粘贴到【页脚 HTML 代码】（如没开通 js 权限请先开通，理由填“适度美化博客”）。

```html
<!-- @format -->

<script src="https://guangzan.gitee.io/awescnb/index.js"></script>
<script>
  const opts = {
    // 基本配置
    theme: {
      name: 'reacg',
      color: '#88b8f5',
      title: '',
      avatar: 'https://gitee.com/peterwd/pic-oss/raw/master/image/202112031032364.jpeg',
      favicon: 'https://gitee.com/peterwd/pic-oss/raw/master/image/202112031032364.jpeg',
      headerBackground: 'https://api.uomg.com/api/rand.avatar',
      log: false,
    },
    // 代码高亮
    highLight: {
      enable: true,
    },
    // 代码行号
    lineNumbers: {
      enable: true,
    },
    // 码云图标
    gitee: {
      enable: true,
      url: 'https://gitee.com/peterwd',
    },
    // 图片灯箱
    imagebox: {
      enable: true,
    },
    // 文章目录
    catalog: {
      enable: true,
    },
    // 右下角按钮组
    tools: {
      enable: true,
    },
    // live2d模型
    live2d: {
      enable: true,
      model: 'haru-01',
    },
    // 点击特效
    click: {
      enable: true,
    },
    // 评论输入框表情
    emoji: {
      enable: true,
    },
    // 暗色模式
    darkMode: {
      enable: true,
      autoDark: false,
      autoLight: false,
    },
    // 音乐播放器
    musicPlayer: {
      enable: true,
      page: 'all',
      agent: 'pc',
      autoplay: false,
      volume: 0.4,
      lrc: {
        enable: true, // 启用歌词
        type: 1, // 1 -> 字符串歌词 3 -> url 歌词
        color: '', // 颜色
      },
      audio: [
        {
          name: '不要说话',
          artist: 'REOL',
          url: 'http://music.163.com/song/media/outer/url?id=25906124.mp3',
          cover: 'https://guangzan.gitee.io/imagehost/awescnb/music/demo.jpg',
          lrc: ``,
        },
        {
          name: '这世界那么多人',
          artist: 'REOL',
          url: 'http://music.163.com/song/media/outer/url?id=1842025914.mp3',
          cover: 'https://gitee.com/peterwd/pic-oss/raw/master/image/202112031124807.jpeg',
          lrc: ``,
        },
        {
          name: '盛夏的果实',
          artist: 'REOL',
          url: 'http://music.163.com/song/media/outer/url?id=277382.mp3',
          cover: 'https://gitee.com/peterwd/pic-oss/raw/master/image/202112031128356.jpg',
          lrc: ``,
        },
      ],
    },
    // 随笔头图
    postTopimage: {
      enable: true,
    },
    // 随笔尾图
    postBottomimage: {
      enable: true,
    },
    // 打赏二维码
    donation: {
      enable: false,
      qrcodes: [],
    },
    // 个性签名
    signature: {
      enable: false,
      contents: [],
    },
    // 侧边栏二维码
    qrcode: {
      enable: false,
      img: '',
      desc: '',
    },

    // 随笔页尾部签名
    postSignature: {
      enable: true,
      content: [],
      licenseName: '',
      licenseLink: '',
    },
    // 背景图片或颜色
    bodyBackground: {
      enable: true,
      value: '#88b8f5',
      opacity: 1,
      repeat: false,
    },
    // 自定义链接链接
    links: [
      {
        name: '自定义链接',
        link: '',
      },
    ],
  }
  $.awesCnb(opts)
</script>
```

![image-20211203194745816](https://gitee.com/peterwd/pic-oss/raw/master/image/202112031947293.png)

6. 点击保存，进入你的博客查看效果。



参考文档

https://www.yuque.com/awescnb/user/tmpomo

