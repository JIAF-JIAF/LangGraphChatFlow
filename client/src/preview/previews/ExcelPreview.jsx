import { useState, useEffect } from 'react';
import { convertExcelToWorkbook } from '../utils/excelConverter/index.js';

export const ExcelPreview = ({ blob }) => {
  const [workbook, setWorkbook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const ZONGHENG = window.ZONGHENG || {};
  const { SheetApplicationProvider, SheetApplication } = ZONGHENG;

  useEffect(() => {
    const loadExcel = async () => {
      if (!blob) return;

      setLoading(true);
      setError(null);

      try {
        const arrayBuffer = await blob.arrayBuffer();
        const zhWorkbook = await convertExcelToWorkbook(arrayBuffer);
        setWorkbook(zhWorkbook);
        setLoading(false);
      } catch (err) {
        setError(err.message || 'Excel 文件解析失败');
        setLoading(false);
      }
    };

    loadExcel();
  }, [blob]);

  if (!SheetApplicationProvider || !SheetApplication) {
    return (
      <div className="excel-error">
        <span>Excel 预览功能需要在向量库管理页面使用</span>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="excel-loading">
        <div className="spinner"></div>
        <span>加载 Excel 文件...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="excel-error">
        <span className="error-icon">❌</span>
        <p>{error}</p>
      </div>
    );
  }

  if (!workbook) {
    return <div className="excel-empty">Excel 文件为空</div>;
  }

  return (
    <SheetApplicationProvider
      workbook={workbook}
      style={{ height: '100%', width: '100%' }}
    >
      <SheetApplication
        sheetConfig={{
          header: true,
          enableScale: true,
          enableSelection: true,
        }}
      />
    </SheetApplicationProvider>
  );
};
