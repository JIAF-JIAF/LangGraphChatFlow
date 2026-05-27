import React, { useMemo, useEffect, useState, Suspense } from 'react';

let cangjieInstance = null;

const initCangjie = () => {
  if (cangjieInstance) {
    return cangjieInstance;
  }
  
  const { Provider, Content, createZhi, presetZhi, zhi_locale_zh_CN } = window.CangjieSetup || {};
  const { createSerializer } = window.Cangjie || {};
  
  if (!Provider || !Content || !createZhi || !presetZhi || !zhi_locale_zh_CN || !createSerializer) {
    return null;
  }
  
  try {
    const config = {
      marks: {
        bold: true,
        italic: true,
        underline: true,
        strikethrough: true,
        color: true,
        fontSize: true,
        backgroundColor: true,
        fontFamily: true,
      },
      nodeAttributes: {
        align: true,
        indent: true,
      }
    };
    
    const plugins = createZhi(presetZhi, config, zhi_locale_zh_CN);
    const mo = createSerializer(plugins);
    
    cangjieInstance = { Provider, Content, plugins, mo };
    return cangjieInstance;
  } catch (e) {
    console.error('仓颉编辑器初始化失败:', e);
    return null;
  }
};

const CangjieContent = ({ plugins, value }) => {
  const { Provider, Content } = cangjieInstance;
  
  return (
    <Provider plugins={plugins} value={value}>
      <Content style={{ padding: 16, minHeight: 400 }} />
    </Provider>
  );
};

export const WordPreview = ({ wordData }) => {
  const [instance, setInstance] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const check = () => {
      const inst = initCangjie();
      if (inst) {
        setInstance(inst);
        setLoading(false);
      } else {
        setTimeout(check, 100);
      }
    };
    check();
    
    const timer = setTimeout(() => {
      if (!instance) {
        console.error('仓颉编辑器加载超时');
        setLoading(false);
      }
    }, 10000);
    
    return () => clearTimeout(timer);
  }, []);
  
  useEffect(() => {
    if (wordData) {
      console.log('Word data received:', JSON.stringify(wordData, null, 2).substring(0, 2000));
    }
  }, [wordData]);
  
  const value = useMemo(() => {
    if (!instance || !wordData) return null;
    
    try {
      const result = instance.mo.jsonMLToValue(wordData);
      console.log('Converted value:', result);
      return result;
    } catch (e) {
      console.error('数据转换失败:', e);
      return null;
    }
  }, [wordData, instance]);
  
  if (!wordData) {
    return (
      <div className="word-preview-empty">
        <span>文件内容为空</span>
      </div>
    );
  }
  
  if (loading) {
    return (
      <div className="word-preview-loading">
        <div className="spinner"></div>
        <span>编辑器加载中...</span>
      </div>
    );
  }
  
  if (!instance) {
    return (
      <div className="word-preview-empty">
        <span>仓颉编辑器初始化失败</span>
      </div>
    );
  }
  
  if (!value) {
    return (
      <div className="word-preview-empty">
        <span>无法解析文档内容</span>
      </div>
    );
  }
  
  return (
    <div className="word-preview-container">
      <Suspense fallback={<div className="word-preview-loading"><div className="spinner"></div><span>渲染中...</span></div>}>
        <CangjieContent plugins={instance.plugins} value={value} />
      </Suspense>
    </div>
  );
};
