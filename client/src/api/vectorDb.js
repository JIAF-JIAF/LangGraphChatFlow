import axios from 'axios';

const BASE_URL = '/api';

const vectorDbApi = {
  getDatabases: async () => {
    const response = await axios.get(`${BASE_URL}/databases`);
    return response.data;
  },

  getDatabase: async (dbName) => {
    const response = await axios.get(`${BASE_URL}/databases/${dbName}`);
    return response.data;
  },

  createDatabase: async (name, description) => {
    const response = await axios.post(`${BASE_URL}/databases`, {
      name,
      description
    });
    return response.data;
  },

  updateDatabase: async (dbName, description) => {
    const response = await axios.put(`${BASE_URL}/databases/${dbName}`, {
      description
    });
    return response.data;
  },

  deleteDatabase: async (dbName) => {
    const response = await axios.delete(`${BASE_URL}/databases/${dbName}`);
    return response.data;
  },

  uploadFiles: async (dbName, files) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await axios.post(
      `${BASE_URL}/databases/${dbName}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    return response.data;
  },

  getDocuments: async (dbName) => {
    const response = await axios.get(`${BASE_URL}/databases/${dbName}/documents`);
    return response.data;
  },

  deleteDocument: async (dbName, docName) => {
    const response = await axios.delete(`${BASE_URL}/databases/${dbName}/documents/${docName}`);
    return response.data;
  },

  getDocumentContent: async (dbName, docName) => {
    const response = await axios.get(`${BASE_URL}/databases/${dbName}/documents/${docName}`, {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default vectorDbApi;