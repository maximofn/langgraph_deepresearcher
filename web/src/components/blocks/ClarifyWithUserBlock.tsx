import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';

/**
 * Parses the raw content string produced by the scope agent:
 *   need_clarification=True question='...' verification=''
 *   need_clarification=False question='' verification='...'
 */
function parseClarifyContent(content: string) {
  const needsClarification =
    /need_clarification=(True|False)/.exec(content)?.[1] === 'True';

  // question value sits between question=' and ' verification='
  const questionMatch = /question='(.*?)'\s+verification='/s.exec(content);
  const question = questionMatch?.[1] ?? '';

  // verification value sits between verification=' and the closing '
  const verificationMatch = /verification='(.*)'$/s.exec(content);
  const verification = verificationMatch?.[1] ?? '';

  return { needsClarification, question, verification };
}

export function ClarifyWithUserBlock({ event }: { event: ResearchEvent }) {
  const cfg = getBlockConfig(event.message_type);
  const { needsClarification, question, verification } = parseClarifyContent(
    event.content || ''
  );

  const label = needsClarification ? 'Need clarification' : 'Not clarification needed';
  const body = needsClarification ? question : verification;

  return (
    <BlockShell
      color={cfg.color}
      cardBg={cfg.cardBg}
      title={cfg.title}
      agent={event.agent}
      copyText={body}
    >
      <div className="space-y-1.5">
        <p className="font-semibold" style={{ color: cfg.color }}>
          {label}
        </p>
        <p className="whitespace-pre-wrap break-words">{body}</p>
      </div>
    </BlockShell>
  );
}
