import { useState, useEffect } from 'react';
import VectorDBManager from './components/VectorDBManager';
import vectorDbApi from './api/vectorDb';
import './App.css';

function DbApp() {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadDatabases();
  }, []);

  const loadDatabases = async () => {
    setLoading(true);
    try {
      const response = await vectorDbApi.getDatabases();
      if (response.status === 'success') {
        setDatabases(response.data);
        if (response.data.length > 0 && !selectedDb) {
          setSelectedDb(response.data[0].name);
        }
        setMessage(null);
      } else {
        setMessage({ type: 'error', text: response.message || '加载数据库列表失败' });
      }
    } catch (error) {
      console.error('加载数据库失败:', error);
      setMessage({ type: 'error', text: '加载数据库列表失败' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDatabase = async (name, description) => {
    try {
      const response = await vectorDbApi.createDatabase(name, description);
      if (response.status === 'success') {
        setMessage({ type: 'success', text: '数据库创建成功' });
        loadDatabases();
      } else {
        setMessage({ type: 'error', text: response.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '创建数据库失败' });
    }
  };

  const handleDeleteDatabase = async (dbName) => {
    try {
      const response = await vectorDbApi.deleteDatabase(dbName);
      if (response.status === 'success') {
        setMessage({ type: 'success', text: '数据库删除成功' });
        if (selectedDb === dbName) {
          setSelectedDb(null);
        }
        loadDatabases();
      } else {
        setMessage({ type: 'error', text: response.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '删除数据库失败' });
    }
  };

  const handleUpdateDatabase = async (dbName, description) => {
    try {
      const response = await vectorDbApi.updateDatabase(dbName, description);
      if (response.status === 'success') {
        setMessage({ type: 'success', text: '数据库信息更新成功' });
        loadDatabases();
      } else {
        setMessage({ type: 'error', text: response.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '更新数据库失败' });
    }
  };

  const handleUploadFiles = async (dbName, files) => {
    try {
      const response = await vectorDbApi.uploadFiles(dbName, files);
      if (response.status === 'success') {
        setMessage({ type: 'success', text: response.message });
        loadDatabases();
      } else {
        setMessage({ type: 'error', text: response.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '上传文件失败' });
    }
  };

  const handleDeleteDocument = async (dbName, docName) => {
    try {
      const response = await vectorDbApi.deleteDocument(dbName, docName);
      if (response.status === 'success') {
        setMessage({ type: 'success', text: '文档删除成功' });
        loadDatabases();
      } else {
        setMessage({ type: 'error', text: response.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '删除文档失败' });
    }
  };

  const closeMessage = () => {
    setMessage(null);
  };

  return (
    <div className="app-container">
      {message && (
        <div className={`message message-${message.type}`} onClick={closeMessage}>
          {message.text}
        </div>
      )}
      <VectorDBManager
        databases={databases}
        selectedDb={selectedDb}
        setSelectedDb={setSelectedDb}
        loading={loading}
        onCreateDatabase={handleCreateDatabase}
        onDeleteDatabase={handleDeleteDatabase}
        onUpdateDatabase={handleUpdateDatabase}
        onUploadFiles={handleUploadFiles}
        onDeleteDocument={handleDeleteDocument}
      />
    </div>
  );
}

export default DbApp;