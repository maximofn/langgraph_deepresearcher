import { useEffect } from 'react';
import { X } from 'lucide-react';
import { ApiKeysSection, ModelsSection, UserInfoSection } from './SettingsSections';

interface PreferencesModalProps {
  open: boolean;
  onClose: () => void;
}

export function PreferencesModal({ open, onClose }: PreferencesModalProps) {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
      return () => { document.body.style.overflow = ''; };
    }
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/80 p-4">
      <div
        className="my-8 flex w-[560px] max-h-[90vh] flex-col gap-6 rounded-2xl py-7 px-8 overflow-y-auto scrollbar-modal"
        style={{ background: '#111111', border: '1px solid #1A1A1A' }}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">Preferences</h2>
          <button
            onClick={onClose}
            className="flex items-center justify-center transition-opacity hover:opacity-70"
            style={{ color: '#666666' }}
          >
            <X size={18} />
          </button>
        </div>

        <UserInfoSection />
        <ApiKeysSection />
        <ModelsSection />

        <div className="flex flex-col gap-4">
          <hr style={{ borderColor: '#1A1A1A' }} />
          <div className="flex justify-end">
            <button
              type="button"
              onClick={onClose}
              className="rounded-[10px] px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-70"
              style={{ background: '#00FF00', color: '#0A0A0A' }}
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
