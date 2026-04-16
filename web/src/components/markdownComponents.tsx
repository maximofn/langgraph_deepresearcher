/**
 * Shared ReactMarkdown custom components.
 * - All links open in a new tab
 * - rel="nofollow noreferrer noopener" on every link
 */
import type { Components } from 'react-markdown';

export const markdownComponents: Components = {
  a: ({ href, children, ...props }) => (
    <a
      href={href}
      target="_blank"
      rel="nofollow noreferrer noopener"
      {...props}
    >
      {children}
    </a>
  ),
};
