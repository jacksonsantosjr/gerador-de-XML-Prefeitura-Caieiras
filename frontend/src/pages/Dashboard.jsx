import React, { useState, useCallback } from 'react';
import { UploadCloud, FileType, CheckCircle, AlertCircle, Loader2, Download } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [competencia, setCompetencia] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);

  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles?.length > 0) {
      setFile(acceptedFiles[0]);
      setErro(null);
      setResultado(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  const handleProcessar = async () => {
    if (!file || !competencia) {
      setErro('Por favor, defina a competência (Mês/Ano) e envie um arquivo válido.');
      return;
    }

    setIsProcessing(true);
    setErro(null);
    setResultado(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('competencia', competencia);

    try {
      // Usa a variável de ambiente VITE_API_URL na Vercel, ou localhost rodando local
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      
      const response = await fetch(`${apiUrl}/api/processar`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro no processamento da nota');
      }

      const totalNotas = response.headers.get('X-Total-Notas') || 'N/A';
      const novosClientes = response.headers.get('X-Novos-Clientes') || '0';

      // Tratamento the Blob pra Download
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      
      setResultado({
        totalNotas,
        novosClientes,
        downloadUrl,
        filename: `Lote_XML_${competencia.replace('-', '_')}.xml`
      });

    } catch (err) {
      setErro(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
      {/* Header Info */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-md p-6 md:p-8 shadow-sm dark:shadow-2xl overflow-hidden relative transition-colors duration-300">
        <div className="absolute top-0 right-0 p-32 bg-emerald-500 opacity-[0.03] dark:opacity-[0.05] rounded-full blur-3xl translate-x-10 -translate-y-10 pointer-events-none"></div>
        
        <div className="relative z-10 grid gap-6 md:grid-cols-2">
          
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-1 tracking-tight">Novo Faturamento em Lote</h2>
            <p className="text-slate-500 dark:text-slate-400 text-sm max-w-sm">
              Faça upload do relatório bruto do ERP. A inteligência cruza os CNPJs com a BrasilAPI e com a sua base para montar o XML exigido pela Prefeitura de Caieiras automaticamente.
            </p>
          </div>

          <div className="bg-slate-50 dark:bg-slate-900/50 p-5 rounded-md border border-slate-200 dark:border-slate-800 backdrop-blur-sm self-center transition-colors duration-300">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Competência (Mês/Ano)</label>
            <input 
              type="month"
              value={competencia}
              onChange={(e) => setCompetencia(e.target.value)}
              className="w-full bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-600 rounded-md px-4 py-2.5 text-slate-700 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all duration-300"
            />
            <p className="text-xs text-slate-500 mt-2">Data exigida no Cabeçalho (Cabecalho &gt; DataCompetencia) do RPS</p>
          </div>
        </div>
      </div>

      {/* Área de Drag & Drop */}
      <div 
        {...getRootProps()} 
        className={`relative border-2 border-dashed rounded-md p-10 transition-all cursor-pointer flex flex-col items-center justify-center text-center duration-300
          ${isDragActive ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10' : 'border-slate-200 dark:border-slate-800 hover:border-emerald-400 dark:hover:border-slate-600 bg-white dark:bg-slate-900/50 hover:bg-slate-50 dark:hover:bg-slate-900'}
          ${file ? 'border-emerald-500 bg-emerald-50 dark:border-emerald-500/50 dark:bg-emerald-500/5' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="h-16 w-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4 shadow-sm dark:shadow-inner ring-1 ring-slate-200 dark:ring-white/10 group-hover:ring-emerald-500/50 transition-all">
          {file ? (
            <FileType className="h-8 w-8 text-emerald-500 dark:text-emerald-400" />
          ) : (
            <UploadCloud className={`h-8 w-8 ${isDragActive ? 'text-emerald-500 dark:text-emerald-400 animate-bounce' : 'text-slate-400'}`} />
          )}
        </div>
        
        {file ? (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">Arquivo Selecionado com Sucesso</p>
            <p className="text-lg font-medium text-slate-800 dark:text-white">{file.name}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">{(file.size / 1024).toFixed(2)} KB • Clique novamente para trocar</p>
          </div>
        ) : (
          <div className="space-y-1">
            <p className="text-base font-medium text-slate-700 dark:text-slate-200">Arraste a Planilha do ERP para cá</p>
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
              Ou clique para selecionar. Formatos suportados: Excel (.xlsx, .xls) ou .CSV
            </p>
          </div>
        )}
      </div>

      {/* Erros da API / Validação */}
      {erro && (
        <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-md p-4 flex items-start space-x-3 text-red-600 dark:text-red-400 duration-300">
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <p className="text-sm">{erro}</p>
        </div>
      )}

      {/* Botão Global de Ação */}
      <button
        onClick={handleProcessar}
        disabled={!file || !competencia || isProcessing}
        className={`w-full py-4 px-6 rounded-md font-semibold text-lg flex items-center justify-center transition-all duration-300
          ${(!file || !competencia) 
            ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 cursor-not-allowed border border-slate-200 dark:border-slate-700' 
            : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md dark:shadow-emerald-900/50 hover:shadow-lg dark:hover:shadow-emerald-900/80 hover:-translate-y-0.5'
          }
        `}
      >
        {isProcessing ? (
          <>
            <Loader2 className="animate-spin h-5 w-5 mr-3" />
            Processando Lote de RPS...
          </>
        ) : (
          <>
            Gerar Lote de Faturamento XML
          </>
        )}
      </button>

      {/* Cards de Sucesso / Resultado Dinâmicos */}
      {resultado && (
        <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-500/30 rounded-md p-6 sm:p-8 mt-8 animate-in zoom-in-95 duration-500">
          <div className="flex items-center space-x-4 mb-6">
            <div className="bg-emerald-100 dark:bg-emerald-500/20 p-2 rounded-full">
              <CheckCircle className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-emerald-700 dark:text-emerald-400">Sucesso Absoluto!</h3>
              <p className="text-emerald-600/80 dark:text-slate-300 text-sm">Estrutura ABRASF Montada Corretamente</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
             <div className="bg-white dark:bg-slate-800/80 rounded-md p-4 border border-emerald-100 dark:border-slate-700 shadow-sm transition-colors duration-300">
                <span className="text-slate-500 dark:text-slate-400 text-xs uppercase tracking-wider font-semibold">Notas Fiscais Processadas</span>
                <p className="text-3xl font-bold text-slate-800 dark:text-white mt-1">{resultado.totalNotas}</p>
             </div>
             <div className="bg-white dark:bg-slate-800/80 rounded-md p-4 border border-emerald-100 dark:border-slate-700 shadow-sm transition-colors duration-300">
                <span className="text-slate-500 dark:text-slate-400 text-xs uppercase tracking-wider font-semibold">Novos CNPJs Validados</span>
                <p className="text-3xl font-bold text-emerald-600 dark:text-amber-400 mt-1">+{resultado.novosClientes}</p>
             </div>
          </div>

          <a 
            href={resultado.downloadUrl}
            download={resultado.filename}
            className="w-full sm:w-auto inline-flex items-center justify-center bg-emerald-600 dark:bg-white text-white dark:text-emerald-900 font-bold px-8 py-3 rounded-md hover:bg-emerald-700 dark:hover:bg-emerald-50 transition-colors shadow-md dark:shadow-xl"
          >
            <Download className="h-5 w-5 mr-2" />
            BAIXAR ARQUIVO FINAL XML
          </a>
        </div>
      )}
    </div>
  );
}
