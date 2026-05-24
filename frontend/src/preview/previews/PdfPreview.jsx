import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export const PdfPreview = ({ blob, onError }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  };

  return (
    <div className="pdf-content">
      <Document
        file={blob}
        onLoadSuccess={onDocumentLoadSuccess}
        onLoadError={(error) => {
          if (onError) onError(error.message);
        }}
        loading={<div className="preview-loading"><div className="spinner"></div><span>PDF 加载中...</span></div>}
        error={<div className="preview-error"><span className="error-icon">❌</span><p>PDF 加载失败</p></div>}
      >
        <Page 
          pageNumber={pageNumber} 
          renderTextLayer={true}
          renderAnnotationLayer={true}
        />
      </Document>
      {numPages && (
        <div className="pdf-controls">
          <button
            className="btn btn-sm"
            disabled={pageNumber <= 1}
            onClick={() => setPageNumber(pageNumber - 1)}
          >
            上一页
          </button>
          <span className="page-info">
            {pageNumber} / {numPages}
          </span>
          <button
            className="btn btn-sm"
            disabled={pageNumber >= numPages}
            onClick={() => setPageNumber(pageNumber + 1)}
          >
            下一页
          </button>
        </div>
      )}
    </div>
  );
};
