import React from 'react';
import { ArrowRight, FileText } from 'lucide-react';

const Hero = ({ onAccess, isExiting }) => {
  return (
    <section className={`hero ${isExiting ? 'exit' : ''}`}>
      <div className="hero-content">
        <div className="hero-badge">
          <FileText size={16} />
          <span>Tecnologia de Conversão</span>
        </div>
        <h1 className="hero-title">
          Conversão RPS <br />
          <span className="text-gradient">XML Prefeitura de Caieiras</span>
        </h1>
        <p className="hero-subtitle">
          Conversão inteligente dos RPS extraídos do ERP Totvs RM na estrutura atualizada exigida pela Prefeitura de Caieiras.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary btn-lg hero-btn" onClick={onAccess}>
            Acessar Ferramenta
            <ArrowRight size={20} />
          </button>
        </div>
      </div>
    </section>
  );
};

export default Hero;
