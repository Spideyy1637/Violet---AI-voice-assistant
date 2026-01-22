import { useEffect } from 'react';
import Icon from '../AppIcon';
import { Checkbox } from './Checkbox';
import Select from './Select';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  settings: any;
  onUpdateSettings: (key: string, value: boolean | string) => void;
}

const SettingsPanel = ({ isOpen, onClose, settings, onUpdateSettings }: SettingsPanelProps) => {

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e?.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  const handleSettingChange = (key: string, value: boolean | string) => {
    console.log(`[SettingsPanel] handleSettingChange: key=${key}, value=${value}`);
    onUpdateSettings(key, value);
  };

  const themeOptions = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'system', label: 'System' }
  ];

  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' }
  ];

  const voiceSpeedOptions = [
    { value: 'slow', label: 'Slow' },
    { value: 'normal', label: 'Normal' },
    { value: 'fast', label: 'Fast' }
  ];

  return (
    <>
      <div
        className={`settings-backdrop ${isOpen ? 'open' : 'closed'}`}
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className={`settings-panel ${isOpen ? 'open' : 'closed'}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="settings-title"
      >
        <div className="settings-header">
          <h2 id="settings-title" className="settings-title">Settings</h2>
          <button
            className="settings-close"
            onClick={onClose}
            aria-label="Close settings"
          >
            <Icon name="X" size={20} />
          </button>
        </div>

        <div className="settings-content">
          <section className="settings-section">
            <h3 className="settings-section-title">Voice Settings</h3>

            <div className="settings-item">
              <div className="settings-item-label">
                <span className="settings-item-title">Voice Input</span>
                <span className="settings-item-description">
                  Enable voice-to-text input
                </span>
              </div>
              <Checkbox
                checked={settings?.voiceEnabled}
                onChange={(e) => handleSettingChange('voiceEnabled', e?.target?.checked)}
              />
            </div>

            <div className="settings-item">
              <div className="settings-item-label">
                <span className="settings-item-title">Auto-send</span>
                <span className="settings-item-description">
                  Automatically send after voice input
                </span>
              </div>
              <Checkbox
                checked={settings?.autoSend}
                onChange={(e) => handleSettingChange('autoSend', e?.target?.checked)}
              />
            </div>

            <div className="settings-item">
              <div className="settings-item-label">
                <span className="settings-item-title">Sound Effects</span>
                <span className="settings-item-description">
                  Play sounds for voice feedback
                </span>
              </div>
              <Checkbox
                checked={settings?.soundEffects}
                onChange={(e) => handleSettingChange('soundEffects', e?.target?.checked)}
              />
            </div>

            <div className="settings-select-wrapper">
              <Select
                label="Voice Speed"
                options={voiceSpeedOptions}
                value={settings?.voiceSpeed}
                onChange={(value) => handleSettingChange('voiceSpeed', value)}
              />
            </div>
          </section>

          <section className="settings-section">
            <h3 className="settings-section-title">Display Preferences</h3>

            <div className="settings-select-wrapper">
              <Select
                label="Theme"
                description="Choose your preferred color scheme"
                options={themeOptions}
                value={settings?.theme}
                onChange={(value) => handleSettingChange('theme', value)}
              />
            </div>

            <div className="settings-select-wrapper">
              <Select
                label="Language"
                description="Select interface language"
                options={languageOptions}
                value={settings?.language}
                onChange={(value) => handleSettingChange('language', value)}
              />
            </div>
          </section>

          <section className="settings-section">
            <h3 className="settings-section-title">Notifications</h3>

            <div className="settings-item">
              <div className="settings-item-label">
                <span className="settings-item-title">Push Notifications</span>
                <span className="settings-item-description">
                  Receive notifications for new messages
                </span>
              </div>
              <Checkbox
                checked={settings?.notifications}
                onChange={(e) => handleSettingChange('notifications', e?.target?.checked)}
              />
            </div>
          </section>

          <section className="settings-section">
            <h3 className="settings-section-title">About</h3>

            <div className="settings-about">
              <div className="settings-item">
                <span className="settings-item-title">Version</span>
                <span className="settings-item-value">1.0.0</span>
              </div>

              <div className="settings-item">
                <span className="settings-item-title">Last Updated</span>
                <span className="settings-item-value">January 2026</span>
              </div>

              <button className="settings-help-btn">
                <Icon name="HelpCircle" size={16} />
                <span>Help & Support</span>
              </button>
            </div>
          </section>
        </div>
      </div>

      <style>{`
        .settings-backdrop {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 100;
          opacity: 0;
          visibility: hidden;
          transition: all 0.2s ease;
        }

        .settings-backdrop.open {
          opacity: 1;
          visibility: visible;
        }

        .settings-panel {
          position: fixed;
          top: 0;
          right: 0;
          bottom: 0;
          width: 100%;
          max-width: 400px;
          background: var(--bg-deep); /* Changed from #111827 to var */
          z-index: 101;
          display: flex;
          flex-direction: column;
          transform: translateX(100%);
          transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          box-shadow: -10px 0 30px rgba(0, 0, 0, 0.3);
          border-left: 1px solid var(--glass-border);
        }

        .settings-panel.open {
          transform: translateX(0);
        }

        .settings-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 20px 24px;
          border-bottom: 1px solid var(--glass-border); /* Changed from #374151 */
          flex-shrink: 0;
        }

        .settings-title {
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary); /* Changed from #ffffff */
          margin: 0;
        }

        .settings-close {
          width: 36px;
          height: 36px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: transparent;
          border: none;
          color: var(--text-muted); /* Changed from #9ca3af */
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .settings-close:hover {
          background: var(--bg-surface);
          color: var(--text-primary);
        }

        .settings-content {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
        }

        .settings-section {
          margin-bottom: 32px;
        }

        .settings-section:last-child {
          margin-bottom: 0;
        }

        .settings-section-title {
          font-size: 12px;
          font-weight: 600;
          color: var(--text-muted); /* Changed from #9ca3af */
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin: 0 0 16px 0;
        }

        .settings-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 0;
          border-bottom: 1px solid var(--glass-border); /* Changed #1f2937 */
        }

        .settings-item:last-child {
          border-bottom: none;
        }

        .settings-item-label {
          flex: 1;
          margin-right: 16px;
        }

        .settings-item-title {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary); /* Changed #f3f4f6 */
        }

        .settings-item-description {
          display: block;
          font-size: 12px;
          color: var(--text-secondary); /* Changed #6b7280 */
          margin-top: 2px;
        }

        .settings-item-value {
          font-size: 14px;
          color: var(--text-muted);
        }

        .settings-select-wrapper {
          margin-top: 16px;
        }

        .settings-about {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .settings-help-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          width: 100%;
          margin-top: 16px;
          padding: 12px 16px;
          background: var(--bg-surface);
          border: 1px solid var(--glass-border);
          border-radius: 8px;
          color: var(--text-secondary);
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .settings-help-btn:hover {
          background: var(--bg-deep);
          color: var(--text-primary);
        }

        @media (max-width: 480px) {
          .settings-panel {
            max-width: 100%;
          }
        }
      `}</style>
    </>
  );
};

export default SettingsPanel;
