import React from 'react';
import { useToast } from '../../hooks/use-toast';

export function Toaster() {
    const { toasts, dismiss } = useToast();

    return (
        <div className="toast-container">
            {toasts.map((toast) => (
                <Toast
                    key={toast.id}
                    toast={toast}
                    onClose={() => dismiss(toast.id)}
                />
            ))}
        </div>
    );
}

function Toast({ toast, onClose }) {
    const { title, description, variant } = toast;

    return (
        <div className={`toast ${variant === 'destructive' ? 'toast-destructive' : 'toast-default'}`}>
            <div className="toast-content">
                {title && <div className="toast-title">{title}</div>}
                {description && <div className="toast-description">{description}</div>}
            </div>
            <button
                className="toast-close"
                onClick={onClose}
                aria-label="Close notification"
            >
                ×
            </button>
        </div>
    );
}