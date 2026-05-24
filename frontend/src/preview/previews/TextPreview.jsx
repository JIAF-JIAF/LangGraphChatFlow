export const TextPreview = ({ content }) => {
  return (
    <pre className="text-content">
      {content || '文件内容为空'}
    </pre>
  );
};
