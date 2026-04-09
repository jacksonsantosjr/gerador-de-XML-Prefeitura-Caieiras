import React, { useState, useCallback, useEffect } from 'react';
import { UploadCloud, FileType, CheckCircle, AlertCircle, Loader2, Download, ExternalLink, Search, X, AlertTriangle, Database, Info } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

export default function Dashboard({ showTomadoresExtra, onCloseTomadores }) {
  const [file, setFile] = useState(null);
  const [competencia, setCompetencia] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);
  
  // Modais
  const [showWarningsModal, setShowWarningsModal] = useState(false);
  const [showTomadoresModal, setShowTomadoresModal] = useState(false);
  const [tomadores, setTomadores] = useState([]);
  const [isLoadingTomadores, setIsLoadingTomadores] = useState(false);
  const [searchTomador, setSearchTomador] = useState('');

  // Modal de Correção
  const [showCorrectionModal, setShowCorrectionModal] = useState(false);
  const [currentWarning, setCurrentWarning] = useState(null);
  const [correctionValue, setCorrectionValue] = useState('');
  const [isSavingCorrection, setIsSavingCorrection] = useState(false);

  // Sincroniza com prop do App.jsx (quando clica no Header)
  useEffect(() => {
    if (showTomadoresExtra) {
      handleOpenTomadores();
    }
  }, [showTomadoresExtra]);

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
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      
      const response = await fetch(`${apiUrl}/api/processar`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro no processamento da nota');
      }

      const data = await response.json();
      
      // Converte base64 de volta para blob para download
      const byteCharacters = atob(data.xml_base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/xml' });
      const downloadUrl = window.URL.createObjectURL(blob);
      
      setResultado({
        totalNotas: data.stats.total_notas,
        novosClientes: data.stats.nov_clientes || data.stats.novos_clientes,
        warnings: data.warnings || [],
        downloadUrl,
        filename: data.filename
      });

    } catch (err) {
      setErro(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleOpenTomadores = async () => {
    setShowTomadoresModal(true);
    setIsLoadingTomadores(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      const response = await fetch(`${apiUrl}/api/tomadores`);
      if (response.ok) {
        const data = await response.json();
        setTomadores(data);
      }
    } catch (err) {
      console.error("Erro ao carregar tomadores:", err);
    } finally {
      setIsLoadingTomadores(false);
    }
  };

  const closeTomadores = () => {
    setShowTomadoresModal(false);
    if (onCloseTomadores) onCloseTomadores();
  };

  const handleNovoProcessamento = () => {
    setFile(null);
    setCompetencia('');
    setResultado(null);
    setErro(null);
  };

  const handleOpenCorrection = (warning) => {
    setCurrentWarning(warning);
    setCorrectionValue(warning.valor_atual === 'Vazio' ? '' : warning.valor_atual);
    setShowCorrectionModal(true);
  };

  const handleSaveCorrection = async () => {
    if (!currentWarning || !correctionValue) return;

    setIsSavingCorrection(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      
      // Mapeamento de campo técnico do XML para campo do Banco
      const fieldMapping = {
        "RazSocTom": "razao_social",
        "LogTom": "logradouro",
        "NumEndTom": "numero",
        "BairroTom": "bairro",
        "MunTom": "municipio",
        "CepTom": "cep"
      };

      const dbField = fieldMapping[currentWarning.field];
      
      const response = await fetch(`${apiUrl}/api/tomadores/${currentWarning.cnpj}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [dbField]: correctionValue })
      });

      if (response.ok) {
        setShowCorrectionModal(false);
        // Reprocessa imediatamente
        handleProcessar();
      } else {
        alert("Erro ao salvar correção.");
      }
    } catch (err) {
      console.error("Erro na correção:", err);
    } finally {
      setIsSavingCorrection(false);
    }
  };

  const filteredTomadores = tomadores.filter(t => 
    t.razao_social?.toLowerCase().includes(searchTomador.toLowerCase()) ||
    t.cnpj?.includes(searchTomador)
  );

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
      {/* Header Info */}
      <div className="bg-white dark:bg-slate-900 border border-stone-300 dark:border-slate-800 rounded-md p-6 md:p-8 shadow-md dark:shadow-2xl overflow-hidden relative transition-colors duration-300">
        <div className="absolute top-0 right-0 p-32 bg-emerald-500 opacity-[0.03] dark:opacity-[0.05] rounded-full blur-3xl translate-x-10 -translate-y-10 pointer-events-none"></div>
        
        <div className="relative z-10 grid gap-6 md:grid-cols-2">
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-stone-800 dark:text-white mb-1 tracking-tight">Novo Envio de RPS em Lote</h2>
            <p className="text-stone-600 dark:text-slate-400 text-sm max-w-sm">
              Faça upload do relatório do ERP para gerar o XML exigido pela Prefeitura de Caieiras.
            </p>
          </div>

          <div className="bg-stone-50 dark:bg-slate-900/50 p-5 rounded-md border border-stone-200 dark:border-slate-800 backdrop-blur-sm self-center transition-colors duration-300">
            <label className="block text-sm font-medium text-stone-700 dark:text-slate-300 mb-2">Competência (Mês/Ano)</label>
            <input 
              type="month"
              value={competencia}
              onChange={(e) => setCompetencia(e.target.value)}
              className="w-full bg-white dark:bg-slate-950 border border-stone-400 dark:border-slate-600 rounded-md px-4 py-2.5 text-stone-800 dark:text-stone-100 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all duration-300 [color-scheme:light] dark:[color-scheme:dark]"
            />
            <p className="text-xs text-stone-600 mt-2">Data exigida no Cabeçalho (SDTRPS &gt; Ano/Mes) do RPS</p>
          </div>
        </div>
      </div>

      {/* Área de Drag & Drop */}
      <div 
        {...getRootProps()} 
        className={`relative border-2 border-dashed rounded-md p-10 transition-all cursor-pointer flex flex-col items-center justify-center text-center duration-300
          ${isDragActive ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10' : 'border-stone-300 dark:border-slate-800 hover:border-emerald-400 dark:hover:border-slate-600 bg-white dark:bg-slate-900/50 hover:bg-stone-50 dark:hover:bg-slate-900'}
          ${file ? 'border-emerald-500 bg-emerald-50 dark:border-emerald-500/50 dark:bg-emerald-500/5' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="h-16 w-16 bg-stone-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4 shadow-sm dark:shadow-inner ring-1 ring-stone-200 dark:ring-white/10 group-hover:ring-emerald-500/50 transition-all">
          {file ? (
            <FileType className="h-8 w-8 text-emerald-500 dark:text-emerald-400" />
          ) : (
            <UploadCloud className={`h-8 w-8 ${isDragActive ? 'text-emerald-500 dark:text-emerald-400 animate-bounce' : 'text-stone-400'}`} />
          )}
        </div>
        
        {file ? (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">Arquivo Selecionado com Sucesso</p>
            <p className="text-lg font-medium text-stone-800 dark:text-white">{file.name}</p>
            <p className="text-xs text-stone-600 dark:text-slate-400">{(file.size / 1024).toFixed(2)} KB • Clique novamente para trocar</p>
          </div>
        ) : (
          <div className="space-y-1">
            <p className="text-base font-medium text-stone-800 dark:text-slate-200">Arraste a Planilha do ERP para cá</p>
            <p className="text-sm text-stone-600 dark:text-slate-400 max-w-sm mx-auto">
              Ou clique para selecionar. Formatos suportados: Excel (.xlsx, .xls) ou .CSV
            </p>
          </div>
        )}
      </div>

      {/* Erros da API / Validação */}
      {erro && (
        <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-md p-4 flex items-start space-x-3 text-red-600 dark:text-red-400">
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <p className="text-sm">{erro}</p>
        </div>
      )}

      {/* Botões de Ação */}
      <div className="flex flex-col sm:flex-row gap-4">
        <button
          onClick={handleProcessar}
          disabled={!file || !competencia || isProcessing}
          className={`flex-1 py-4 px-6 rounded-md font-semibold text-lg flex items-center justify-center transition-all duration-300
            ${(!file || !competencia) 
              ? 'bg-stone-200 dark:bg-slate-800 text-stone-500 dark:text-slate-500 cursor-not-allowed border border-stone-300 dark:border-slate-700' 
              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md'
            }
          `}
        >
          {isProcessing ? (
            <>
              <Loader2 className="animate-spin h-5 w-5 mr-3" />
              Processando Arquivo...
            </>
          ) : (
            <>Gerar Arquivo XML</>
          )}
        </button>

        {file && (
          <button
            onClick={handleNovoProcessamento}
            disabled={isProcessing}
            className="py-4 px-8 rounded-md font-semibold text-lg border border-stone-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-stone-700 dark:text-stone-200 hover:bg-stone-50 dark:hover:bg-slate-700 transition-all shadow-sm"
          >
            Novo Processamento
          </button>
        )}
      </div>

      {/* Cards de Sucesso / Resultado Dinâmicos */}
      {resultado && (
        <div className="space-y-4">
          <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-500/30 rounded-md p-6 sm:p-8 animate-in zoom-in-95 duration-500">
            <div className="flex items-center space-x-4 mb-6">
              <div className="bg-emerald-100 dark:bg-emerald-500/20 p-2 rounded-full">
                <CheckCircle className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-emerald-700 dark:text-emerald-400">Sucesso Absoluto!</h3>
                <p className="text-emerald-600/80 dark:text-slate-300 text-sm">Estrutura de RPS Montada Corretamente</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-white dark:bg-slate-800/80 rounded-md p-4 border border-emerald-100 dark:border-slate-700 shadow-sm">
                <span className="text-stone-600 dark:text-slate-400 text-xs uppercase tracking-wider font-semibold">Notas Fiscais Processadas</span>
                <p className="text-3xl font-bold text-stone-800 dark:text-white mt-1">{resultado.totalNotas}</p>
              </div>
              <div className="bg-white dark:bg-slate-800/80 rounded-md p-4 border border-emerald-100 dark:border-slate-700 shadow-sm">
                <span className="text-stone-600 dark:text-slate-400 text-xs uppercase tracking-wider font-semibold">Novos Tomadores</span>
                <p className="text-3xl font-bold text-emerald-600 dark:text-amber-400 mt-1">+{resultado.novosClientes}</p>
              </div>
            </div>

            {/* Inteligência de Validação - Alerta de Campos Brancos */}
            {resultado.warnings?.length > 0 && (
              <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-500/30 rounded-md p-4 mb-6 flex items-center justify-between animate-pulse">
                <div className="flex items-center space-x-3">
                  <AlertTriangle className="h-6 w-6 text-amber-600 dark:text-amber-400" />
                  <div>
                    <p className="text-amber-800 dark:text-amber-300 font-bold">Atenção: Campos em Branco Detectados!</p>
                    <p className="text-amber-700/80 dark:text-amber-400/80 text-xs">Existem {resultado.warnings.length} inconsistências que podem causar rejeição.</p>
                  </div>
                </div>
                <button 
                  onClick={() => setShowWarningsModal(true)}
                  className="bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold px-4 py-2 rounded-md transition-colors"
                >
                  VERIFICAÇÃO
                </button>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3">
              <a 
                href={resultado.downloadUrl}
                download={resultado.filename}
                className="flex-1 inline-flex items-center justify-center bg-emerald-600 dark:bg-white text-white dark:text-emerald-900 font-bold px-8 py-3 rounded-md hover:bg-emerald-700 dark:hover:bg-emerald-50 transition-colors shadow-md"
              >
                <Download className="h-5 w-5 mr-2" />
                BAIXAR ARQUIVO FINAL XML
              </a>

              <a 
                href="https://nfe.etransparencia.com.br/sp.caieiras/nfe/principal.aspx"
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 inline-flex items-center justify-center bg-stone-800 dark:bg-slate-700 text-white font-bold px-8 py-3 rounded-md hover:bg-stone-900 dark:hover:bg-slate-600 transition-colors shadow-md"
              >
                <ExternalLink className="h-5 w-5 mr-2" />
                VALIDAR ARQUIVO
              </a>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Inteligência de Validação (Warnings) */}
      {showWarningsModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-stone-950/80 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white dark:bg-slate-900 w-full max-w-2xl rounded-md shadow-2xl border border-stone-200 dark:border-slate-800 overflow-hidden animate-in zoom-in-95 duration-300">
            <div className="p-6 border-b border-stone-100 dark:border-slate-800 flex justify-between items-center bg-amber-500/5">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="h-6 w-6 text-amber-500" />
                <h3 className="text-xl font-bold dark:text-white">Relatório de Campos em Branco</h3>
              </div>
              <button onClick={() => setShowWarningsModal(false)} className="p-2 hover:bg-stone-100 dark:hover:bg-stone-800 rounded-full transition-colors">
                <X className="h-5 w-5 dark:text-stone-400" />
              </button>
            </div>
            
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              <div className="space-y-3">
                {resultado.warnings.map((w, idx) => (
                  <div key={idx} className="bg-stone-50 dark:bg-slate-800/50 p-4 rounded border border-stone-100 dark:border-slate-700 flex items-center justify-between group/w">
                    <div>
                      <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase">RPS {w.rps}</span>
                      <p className="text-stone-800 dark:text-stone-200 font-medium">Campo <span className="text-red-500 underline">{w.campo}</span> obrigatório.</p>
                      <p className="text-[10px] text-stone-500">CNPJ: {w.cnpj}</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <button 
                        onClick={() => handleOpenCorrection(w)}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-bold px-3 py-2 rounded transition-all opacity-0 group-hover/w:opacity-100"
                      >
                        CORRIGIR AGORA
                      </button>
                      <div className="text-right">
                        <span className="text-[10px] text-stone-500 block uppercase">Status</span>
                        <span className="bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-[10px] font-bold px-2 py-1 rounded">REJEIÇÃO PROVÁVEL</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 bg-stone-50 dark:bg-slate-900/50 border-t border-stone-100 dark:border-slate-800 text-center">
              <p className="text-sm text-stone-600 dark:text-slate-400 mb-4">
                A prefeitura de Caieiras não aceita campos vazios. Por favor, ajuste os dados na sua planilha ERP antes do envio definitivo.
              </p>
              <button 
                onClick={() => setShowWarningsModal(false)}
                className="w-full bg-stone-800 dark:bg-white text-white dark:text-stone-900 font-bold py-3 rounded-md"
              >
                ENTENDI, VOU CORRIGIR
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Banco de Tomadores (Supabase) */}
      {showTomadoresModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-stone-950/90 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white dark:bg-slate-900 w-full max-w-5xl h-[85vh] rounded-md shadow-2xl border border-stone-200 dark:border-slate-800 flex flex-col overflow-hidden animate-in slide-in-from-bottom-8 duration-500">
            <div className="p-6 border-b border-stone-100 dark:border-slate-800 flex justify-between items-center bg-emerald-600">
              <div className="flex items-center space-x-3 text-white">
                <Database className="h-6 w-6" />
                <div>
                  <h3 className="text-xl font-bold">Base de Tomadores Enriquecida</h3>
                  <p className="text-emerald-100 text-xs">Dados sincronizados com o seu banco de dados Supabase e BrasilAPI</p>
                </div>
              </div>
              <button onClick={closeTomadores} className="p-2 hover:bg-emerald-700/50 rounded-full transition-colors text-white">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 bg-white dark:bg-slate-900 border-b border-stone-100 dark:border-slate-800">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-stone-400" />
                <input 
                  type="text"
                  placeholder="Buscar por Razão Social ou CNPJ..."
                  value={searchTomador}
                  onChange={(e) => setSearchTomador(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-stone-50 dark:bg-slate-950 border border-stone-200 dark:border-stone-700 rounded-md outline-none focus:ring-2 focus:ring-emerald-500 text-stone-700 dark:text-white"
                />
              </div>
            </div>

            <div className="flex-1 overflow-auto p-0">
              {isLoadingTomadores ? (
                <div className="h-full flex flex-col items-center justify-center space-y-4">
                  <Loader2 className="h-12 w-12 text-emerald-600 animate-spin" />
                  <p className="text-stone-500">Consultando Supabase...</p>
                </div>
              ) : (
                <table className="w-full text-left border-collapse">
                  <thead className="sticky top-0 bg-stone-50 dark:bg-slate-800/80 backdrop-blur-md border-b border-stone-200 dark:border-slate-700">
                    <tr>
                      <th className="px-6 py-4 text-xs font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider">CNPJ</th>
                      <th className="px-6 py-4 text-xs font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Razão Social</th>
                      <th className="px-6 py-4 text-xs font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Localidade</th>
                      <th className="px-6 py-4 text-xs font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Bairro</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100 dark:divide-slate-800">
                    {filteredTomadores.map((t, idx) => (
                      <tr key={idx} className="hover:bg-stone-50 dark:hover:bg-slate-800/50 transition-colors group">
                        <td className="px-6 py-4 text-sm font-mono text-stone-600 dark:text-stone-300 font-bold group-hover:text-emerald-600">{t.cnpj}</td>
                        <td className="px-6 py-4 text-sm text-stone-800 dark:text-stone-200 font-medium">{t.razao_social}</td>
                        <td className="px-6 py-4 text-sm text-stone-600 dark:text-stone-400">{t.municipio} - {t.uf}</td>
                        <td className="px-6 py-4 text-sm text-stone-600 dark:text-stone-400 italic">{t.bairro || 'Não informado'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <div className="p-4 bg-stone-50 dark:bg-slate-900/50 border-t border-stone-100 dark:border-slate-800 flex justify-between items-center">
              <span className="text-sm text-stone-600">{filteredTomadores.length} registros encontrados</span>
              <button 
                onClick={closeTomadores}
                className="bg-emerald-600 text-white px-6 py-2 rounded-md font-bold text-sm"
              >
                FECHAR
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Correção Rápida */}
      {showCorrectionModal && (
        <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-stone-950/80 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white dark:bg-slate-900 w-full max-w-md rounded-md shadow-2xl border border-stone-200 dark:border-slate-800 overflow-hidden">
            <div className="p-6 border-b border-stone-100 dark:border-slate-800 flex justify-between items-center bg-emerald-600 text-white">
              <div className="flex items-center space-x-2">
                <Info className="h-5 w-5" />
                <h3 className="font-bold">Correção de Tomador</h3>
              </div>
              <button onClick={() => setShowCorrectionModal(false)}><X className="h-5 w-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="text-xs font-bold text-stone-600 uppercase">Ajustar o campo:</label>
                <p className="text-stone-800 dark:text-white font-medium">{currentWarning?.campo}</p>
              </div>
              <div>
                <label className="text-xs font-bold text-stone-600 uppercase">Novo Valor:</label>
                <input 
                  type="text"
                  value={correctionValue}
                  onChange={(e) => setCorrectionValue(e.target.value)}
                  className="w-full mt-1 bg-stone-50 dark:bg-slate-950 border border-stone-300 dark:border-stone-700 rounded-md px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500 text-stone-800 dark:text-white"
                  placeholder={`Digite o ${currentWarning?.campo}...`}
                  autoFocus
                />
              </div>
              <button 
                onClick={handleSaveCorrection}
                disabled={isSavingCorrection || !correctionValue}
                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-md flex items-center justify-center"
              >
                {isSavingCorrection ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <Database className="h-4 w-4 mr-2" />}
                SALVAR E REPROCESSAR
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
