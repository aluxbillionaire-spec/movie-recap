import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ChevronDown, Globe } from 'lucide-react';
import { clsx } from 'clsx';

import { supportedLanguages, getLanguageInfo, isRTL } from '@/i18n';

interface LanguageSelectorProps {
  className?: string;
  variant?: 'default' | 'compact';
  showFlag?: boolean;
  showName?: boolean;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  className,
  variant = 'default',
  showFlag = true,
  showName = true,
}) => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  const currentLanguage = getLanguageInfo(i18n.language);

  const handleLanguageChange = async (languageCode: string) => {
    await i18n.changeLanguage(languageCode);
    setIsOpen(false);

    // Update document direction for RTL languages
    document.dir = isRTL(languageCode) ? 'rtl' : 'ltr';
    
    // Update document language
    document.documentElement.lang = languageCode;
  };

  const isCompact = variant === 'compact';

  return (
    <div className={clsx('relative', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          'flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors',
          isCompact && 'px-2 py-1'
        )}
        aria-label="Select language"
      >
        {showFlag ? (
          <span className="text-lg">{currentLanguage.flag}</span>
        ) : (
          <Globe className="w-4 h-4 text-gray-600" />
        )}
        
        {showName && !isCompact && (
          <span className="text-sm font-medium text-gray-700">
            {currentLanguage.nativeName}
          </span>
        )}
        
        <ChevronDown 
          className={clsx(
            'w-4 h-4 text-gray-400 transition-transform',
            isOpen && 'rotate-180'
          )} 
        />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute top-full mt-1 right-0 bg-white border border-gray-200 rounded-lg shadow-lg z-20 min-w-48 max-h-64 overflow-y-auto">
            <div className="py-1">
              {supportedLanguages.map((language) => (
                <button
                  key={language.code}
                  onClick={() => handleLanguageChange(language.code)}
                  className={clsx(
                    'w-full flex items-center gap-3 px-4 py-2 text-left hover:bg-gray-50 transition-colors',
                    currentLanguage.code === language.code && 'bg-primary-50 text-primary-700'
                  )}
                >
                  <span className="text-lg">{language.flag}</span>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {language.nativeName}
                    </div>
                    <div className="text-xs text-gray-500">
                      {language.name}
                    </div>
                  </div>
                  {currentLanguage.code === language.code && (
                    <div className="w-2 h-2 bg-primary-600 rounded-full" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageSelector;