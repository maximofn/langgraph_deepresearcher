import { useEffect, useState } from 'react';
import { AlertTriangle, Eye, EyeOff, Loader2, Trash2 } from 'lucide-react';
import { api } from '@/api/client';
import {
  DISCOVERY_TTL_MS,
  hashApiKeys,
  useSessionStore,
} from '@/state/sessionStore';

export function UserInfoSection() {
  const userInfo = useSessionStore((s) => s.userInfo);
  const setUserInfo = useSessionStore((s) => s.setUserInfo);

  const handleChange = (field: 'name' | 'email', value: string) => {
    setUserInfo({ ...userInfo, [field]: value });
  };

  return (
    <div className="flex flex-col gap-3">
      <label
        className="font-mono font-medium tracking-widest"
        style={{ fontSize: '11px', color: '#888888' }}
      >
        YOUR INFO
      </label>
      <div
        className="text-[11px]"
        style={{ color: '#666666', lineHeight: '1.4' }}
      >
        Used to deliver the final research report to your inbox when the
        investigation completes. Leave blank if you don't want an email.
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1">
          <span style={{ fontSize: '12px', color: '#AAAAAA' }}>Name</span>
          <input
            type="text"
            value={userInfo.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="Your name"
            autoComplete="name"
            className="w-full rounded-[8px] px-3 py-2 outline-none"
            style={{
              background: '#0A0A0A',
              border: '1px solid #222222',
              color: '#ffffff',
              fontSize: '13px',
            }}
          />
        </div>
        <div className="flex flex-col gap-1">
          <span style={{ fontSize: '12px', color: '#AAAAAA' }}>Email</span>
          <input
            type="email"
            value={userInfo.email}
            onChange={(e) => handleChange('email', e.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            spellCheck={false}
            className="w-full rounded-[8px] px-3 py-2 outline-none"
            style={{
              background: '#0A0A0A',
              border: '1px solid #222222',
              color: '#ffffff',
              fontSize: '13px',
            }}
          />
        </div>
      </div>
    </div>
  );
}

interface ProviderField {
  env: string;
  label: string;
  placeholder: string;
}

const PROVIDER_FIELDS: ProviderField[] = [
  { env: 'OPENAI_API_KEY', label: 'OpenAI', placeholder: 'sk-...' },
  { env: 'ANTHROPIC_API_KEY', label: 'Anthropic', placeholder: 'sk-ant-...' },
  { env: 'GEMINI_API_KEY', label: 'Google Gemini', placeholder: 'AIza...' },
  { env: 'KIMI_K2_API_KEY', label: 'Moonshot Kimi K2', placeholder: 'sk-...' },
  { env: 'CEREBRAS_API_KEY', label: 'Cerebras', placeholder: 'csk-...' },
  { env: 'GITHUB_API_KEY', label: 'GitHub Models', placeholder: 'ghp_...' },
];

const ROLE_LABELS: Record<string, string> = {
  scope: 'Scope',
  supervisor: 'Supervisor',
  research: 'Research',
  compress: 'Compress',
  summarization: 'Summarization',
  writer: 'Writer',
};

const ROLE_DESCRIPTIONS: Record<string, string> = {
  scope:
    'Clarifies your request and turns the conversation into a structured research brief.',
  supervisor:
    'Breaks the brief into topics and delegates them to parallel research sub-agents.',
  research:
    'Runs iterative web searches on an assigned topic and gathers raw findings.',
  compress:
    'Compresses each sub-agent’s raw notes into a concise summary for the supervisor.',
  summarization:
    'Summarizes individual search results to keep the research context lean.',
  writer:
    'Synthesizes all compressed findings into the final markdown report.',
};

export function ApiKeysSection() {
  const apiKeys = useSessionStore((s) => s.apiKeys);
  const setApiKeys = useSessionStore((s) => s.setApiKeys);
  const [revealedKeys, setRevealedKeys] = useState<Record<string, boolean>>({});

  const handleApiKeyChange = (env: string, value: string) => {
    const next = { ...apiKeys, [env]: value };
    if (!value) delete next[env];
    setApiKeys(next);
  };

  const handleClearApiKeys = () => {
    setApiKeys({});
    setRevealedKeys({});
  };

  const toggleReveal = (env: string) => {
    setRevealedKeys({ ...revealedKeys, [env]: !revealedKeys[env] });
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <label
          className="font-mono font-medium tracking-widest"
          style={{ fontSize: '11px', color: '#888888' }}
        >
          API KEYS
        </label>
        <button
          type="button"
          onClick={handleClearApiKeys}
          className="flex items-center gap-1 transition-opacity hover:opacity-70"
          style={{ fontSize: '11px', color: '#888888' }}
        >
          <Trash2 size={11} />
          Clear all
        </button>
      </div>
      <div
        className="text-[11px]"
        style={{ color: '#666666', lineHeight: '1.4' }}
      >
        Stored in your browser only. Sent over HTTPS with each research
        request and never persisted on the server.
      </div>
      <div className="grid grid-cols-2 gap-3">
        {PROVIDER_FIELDS.map(({ env, label, placeholder }) => {
          const revealed = revealedKeys[env] ?? false;
          const value = apiKeys[env] ?? '';
          return (
            <div key={env} className="flex flex-col gap-1">
              <span style={{ fontSize: '12px', color: '#AAAAAA' }}>
                {label}
              </span>
              <div
                className="flex items-center rounded-[8px]"
                style={{
                  background: '#0A0A0A',
                  border: '1px solid #222222',
                }}
              >
                <input
                  type={revealed ? 'text' : 'password'}
                  value={value}
                  onChange={(e) => handleApiKeyChange(env, e.target.value)}
                  placeholder={placeholder}
                  autoComplete="off"
                  spellCheck={false}
                  className="w-full bg-transparent px-3 py-2 outline-none"
                  style={{ fontSize: '13px', color: '#ffffff' }}
                />
                <button
                  type="button"
                  onClick={() => toggleReveal(env)}
                  className="px-2 transition-opacity hover:opacity-70"
                  style={{ color: '#666666' }}
                  tabIndex={-1}
                  aria-label={revealed ? 'Hide key' : 'Show key'}
                >
                  {revealed ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const PROVIDER_LABELS_SHORT: Record<string, string> = {
  OPENAI_API_KEY: 'OpenAI',
  ANTHROPIC_API_KEY: 'Anthropic',
  GEMINI_API_KEY: 'Gemini',
  KIMI_K2_API_KEY: 'Kimi',
  CEREBRAS_API_KEY: 'Cerebras',
  GITHUB_API_KEY: 'GitHub',
};

export function ModelsSection() {
  const modelsCatalog = useSessionStore((s) => s.modelsCatalog);
  const selectedModels = useSessionStore((s) => s.selectedModels);
  const setSelectedModels = useSessionStore((s) => s.setSelectedModels);
  const apiKeys = useSessionStore((s) => s.apiKeys);
  const discoveredCatalog = useSessionStore((s) => s.discoveredCatalog);
  const discoveredCatalogAt = useSessionStore((s) => s.discoveredCatalogAt);
  const discoveredForKeysHash = useSessionStore((s) => s.discoveredForKeysHash);
  const isDiscovering = useSessionStore((s) => s.isDiscovering);
  const discoveryError = useSessionStore((s) => s.discoveryError);
  const setDiscovering = useSessionStore((s) => s.setDiscovering);
  const setDiscoveredCatalog = useSessionStore((s) => s.setDiscoveredCatalog);
  const setDiscoveryError = useSessionStore((s) => s.setDiscoveryError);

  // Trigger a discovery run on mount if the user has API keys and the
  // cache is missing, stale, or was built for a different set of providers.
  useEffect(() => {
    const currentHash = hashApiKeys(apiKeys);
    if (!currentHash) return; // no keys -> nothing to discover

    const stale =
      discoveredCatalogAt === null ||
      Date.now() - discoveredCatalogAt > DISCOVERY_TTL_MS;
    const mismatch = discoveredForKeysHash !== currentHash;

    if (!discoveredCatalog || stale || mismatch) {
      let cancelled = false;
      setDiscovering(true);
      api
        .discoverModels(apiKeys)
        .then((catalog) => {
          if (cancelled) return;
          setDiscoveredCatalog(catalog, currentHash);
        })
        .catch((err) => {
          if (cancelled) return;
          const msg =
            (err && typeof err === 'object' && 'message' in err
              ? String((err as { message: unknown }).message)
              : null) || 'Discovery failed';
          setDiscoveryError(msg);
        });
      return () => {
        cancelled = true;
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const effectiveCatalog = discoveredCatalog ?? modelsCatalog;
  const catalogLoaded = effectiveCatalog !== null;
  const availableModels = effectiveCatalog?.models ?? [];
  const roles = effectiveCatalog?.roles ?? [];

  const filledEnvs = new Set(
    Object.entries(apiKeys)
      .filter(([, v]) => v && v.trim().length > 0)
      .map(([k]) => k),
  );

  const failedProviders = discoveredCatalog?.providers
    ? Object.entries(discoveredCatalog.providers)
        .filter(([, status]) => !status.ok)
        .map(([env]) => PROVIDER_LABELS_SHORT[env] ?? env)
    : [];

  const handleModelChange = (role: string, modelName: string) => {
    setSelectedModels({ ...selectedModels, [role]: modelName });
  };

  return (
    <div className="flex flex-col gap-3">
      <label
        className="font-mono font-medium tracking-widest"
        style={{ fontSize: '11px', color: '#888888' }}
      >
        MODELS PER AGENT
      </label>

      <img
        src="https://images.maximofn.com/DeepResearcher-architecture-all-models.webp"
        alt="DeepResearcher agent architecture"
        className="w-full rounded-[8px] object-contain"
        style={{ border: '1px solid #1A1A1A' }}
      />

      {discoveryError && (
        <div
          className="flex items-start gap-2 rounded-[8px] px-3 py-2"
          style={{
            background: '#2A1A0A',
            border: '1px solid #553311',
            fontSize: '11px',
            color: '#DDAA66',
          }}
        >
          <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
          <span>Discovery failed: {discoveryError}. Showing cached catalog.</span>
        </div>
      )}
      {!discoveryError && failedProviders.length > 0 && (
        <div
          className="flex items-start gap-2 rounded-[8px] px-3 py-2"
          style={{
            background: '#2A1A0A',
            border: '1px solid #553311',
            fontSize: '11px',
            color: '#DDAA66',
          }}
        >
          <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
          <span>Some providers failed: {failedProviders.join(', ')}</span>
        </div>
      )}

      {isDiscovering ? (
        <div
          className="flex items-center justify-center gap-2 rounded-[8px] py-8"
          style={{
            background: '#0A0A0A',
            border: '1px dashed #222222',
            color: '#888888',
            fontSize: '13px',
          }}
        >
          <Loader2 size={16} className="animate-spin" />
          <span>Discovering models…</span>
        </div>
      ) : !catalogLoaded ? (
        <div style={{ fontSize: '12px', color: '#666666' }}>Loading models…</div>
      ) : availableModels.length === 0 ? (
        <div style={{ fontSize: '12px', color: '#CC6666' }}>
          No models available.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {roles.map((role) => (
            <div key={role} className="flex flex-col gap-1">
              <span style={{ fontSize: '12px', color: '#AAAAAA' }}>
                {ROLE_LABELS[role] ?? role}
              </span>
              {ROLE_DESCRIPTIONS[role] && (
                <span
                  style={{
                    fontSize: '11px',
                    color: '#666666',
                    lineHeight: 1.4,
                  }}
                >
                  {ROLE_DESCRIPTIONS[role]}
                </span>
              )}
              <select
                value={selectedModels[role] ?? ''}
                onChange={(e) => handleModelChange(role, e.target.value)}
                className="w-full rounded-[8px] px-3 py-2 outline-none"
                style={{
                  background: '#0A0A0A',
                  border: '1px solid #222222',
                  color: '#ffffff',
                  fontSize: '13px',
                }}
              >
                {availableModels.map((m) => {
                  const hasKey = filledEnvs.has(m.api_key_env);
                  return (
                    <option key={m.name} value={m.name}>
                      {m.label}
                      {hasKey ? '' : ' (missing key)'}
                    </option>
                  );
                })}
              </select>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
