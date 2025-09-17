import React, { useState, useCallback } from 'react';

let toastCounter = 0;

const toastState = {
    toasts: [],
    listeners: new Set(),
};

function notifyListeners() {
    toastState.listeners.forEach(listener => listener(toastState.toasts));
}

function addToast(toast) {
    const id = `toast-${++toastCounter}`;
    const newToast = {
        id,
        title: '',
        description: '',
        variant: 'default',
        duration: 4000,
        ...toast,
    };

    toastState.toasts.push(newToast);
    notifyListeners();

    // Auto dismiss after duration
    if (newToast.duration > 0) {
        setTimeout(() => {
            removeToast(id);
        }, newToast.duration);
    }

    return id;
}

function removeToast(id) {
    toastState.toasts = toastState.toasts.filter(toast => toast.id !== id);
    notifyListeners();
}

function clearAllToasts() {
    toastState.toasts = [];
    notifyListeners();
}

export function useToast() {
    const [toasts, setToasts] = useState(toastState.toasts);

    // Subscribe to toast updates
    React.useEffect(() => {
        toastState.listeners.add(setToasts);
        return () => {
            toastState.listeners.delete(setToasts);
        };
    }, []);

    const toast = useCallback((props) => {
        return addToast(props);
    }, []);

    const dismiss = useCallback((id) => {
        removeToast(id);
    }, []);

    const clear = useCallback(() => {
        clearAllToasts();
    }, []);

    return {
        toast,
        dismiss,
        clear,
        toasts,
    };
}

// Export individual functions for external use
export { addToast as toast, removeToast as dismiss, clearAllToasts as clear };