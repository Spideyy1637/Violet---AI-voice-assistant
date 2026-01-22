import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
    checked?: boolean;
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
    ({ className, checked, onChange, ...props }, ref) => {
        return (
            <label className="checkbox-wrapper">
                <input
                    type="checkbox"
                    ref={ref}
                    checked={checked}
                    onChange={onChange}
                    className={cn("checkbox-input", className)}
                    {...props}
                />
                <span className="checkbox-control">
                    <svg
                        className="checkbox-icon"
                        viewBox="0 0 12 10"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M1 5L4.5 8.5L11 1"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                    </svg>
                </span>
                <style>{`
          .checkbox-wrapper {
            position: relative;
            display: inline-flex;
            align-items: center;
            cursor: pointer;
          }

          .checkbox-input {
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
          }

          .checkbox-control {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid #4b5563;
            background: transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.15s ease;
          }

          .checkbox-input:checked + .checkbox-control {
            background: #3b82f6;
            border-color: #3b82f6;
          }

          .checkbox-input:focus + .checkbox-control {
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
          }

          .checkbox-icon {
            width: 12px;
            height: 12px;
            color: white;
            opacity: 0;
            transform: scale(0.5);
            transition: all 0.15s ease;
          }

          .checkbox-input:checked + .checkbox-control .checkbox-icon {
            opacity: 1;
            transform: scale(1);
          }
        `}</style>
            </label>
        );
    }
);

Checkbox.displayName = 'Checkbox';
