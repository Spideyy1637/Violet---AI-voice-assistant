import { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  label?: string;
  description?: string;
  className?: string;
}

const Select = ({ options, value, onChange, label, description, className }: SelectProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find(opt => opt.value === value);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={cn("select-container", className)} ref={selectRef}>
      {label && (
        <div className="select-label-wrapper">
          <label className="select-label">{label}</label>
          {description && <span className="select-description">{description}</span>}
        </div>
      )}
      <button
        type="button"
        className={cn("select-trigger", isOpen && "open")}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <span>{selectedOption?.label || 'Select...'}</span>
        <ChevronDown size={16} className={cn("select-chevron", isOpen && "rotated")} />
      </button>

      {isOpen && (
        <div className="select-dropdown">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              className={cn("select-option", option.value === value && "selected")}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}

      <style>{`
        .select-container {
          position: relative;
          width: 100%;
        }

        .select-label-wrapper {
          margin-bottom: 8px;
        }

        .select-label {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary); /* Changed #f3f4f6 */
          margin-bottom: 2px;
        }

        .select-description {
          display: block;
          font-size: 12px;
          color: var(--text-muted); /* Changed #9ca3af */
        }

        .select-trigger {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 10px 12px;
          background: var(--bg-surface); /* Changed #1f2937 */
          border: 1px solid var(--glass-border); /* Changed #374151 */
          border-radius: 8px;
          color: var(--text-primary); /* Changed #f3f4f6 */
          font-size: 14px;
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .select-trigger:hover {
          border-color: var(--text-muted); /* Changed #4b5563 */
        }

        .select-trigger.open {
          border-color: var(--neon-blue); /* Changed #3b82f6 */
        }

        .select-chevron {
          color: var(--text-muted); /* Changed #9ca3af */
          transition: transform 0.15s ease;
        }

        .select-chevron.rotated {
          transform: rotate(180deg);
        }

        .select-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          margin-top: 4px;
          background: var(--bg-deep); /* Changed #1f2937 */
          border: 1px solid var(--glass-border); /* Changed #374151 */
          border-radius: 8px;
          padding: 4px;
          z-index: 50;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
          animation: dropdownIn 0.15s ease;
        }

        @keyframes dropdownIn {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .select-option {
          width: 100%;
          padding: 10px 12px;
          background: transparent;
          border: none;
          border-radius: 6px;
          color: var(--text-secondary); /* Changed #d1d5db */
          font-size: 14px;
          text-align: left;
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .select-option:hover {
          background: var(--bg-surface); /* Changed #374151 */
          color: var(--text-primary); /* Changed #ffffff */
          /* box-shadow: 0 0 0 1px var(--glass-border); */
        }

        .select-option.selected {
          background: var(--neon-blue); /* Changed #3b82f6 */
          color: #ffffff;
        }
      `}</style>
    </div>
  );
};

export default Select;
