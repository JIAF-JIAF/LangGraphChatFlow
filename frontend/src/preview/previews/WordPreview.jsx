export const WordPreview = ({ content }) => {
  return (
    <pre className="text-content">
      {content || '文件内容为空'}
    </pre>
  );
};
