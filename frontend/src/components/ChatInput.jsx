import { useRef, useState } from 'react';
import { Icon } from './Icon';

export function ChatInput({ disabled, onSubmit }) {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState([]);
  const fileInputRef = useRef(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || disabled) return;

    onSubmit(trimmed, attachments);
    setMessage('');
    setAttachments([]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleAttachmentChange = (event) => {
    setAttachments(Array.from(event.target.files ?? []));
  };

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <div className="composer-shell">
        {attachments.length > 0 && (
          <div className="attachment-preview-row" aria-label="Selected attachments">
            {attachments.map((file) => (
              <span className="attachment-pill" key={`${file.name}-${file.size}`}>
                <Icon name="file" size={14} />
                {file.name}
              </span>
            ))}
          </div>
        )}

        <div className="composer-input-row">
          <input
            ref={fileInputRef}
            className="sr-only"
            type="file"
            multiple
            accept="image/*,.pdf,.doc,.docx,audio/*,video/*"
            onChange={handleAttachmentChange}
            disabled={disabled}
            aria-label="Attach files"
          />
          <button
            type="button"
            className="composer-icon-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            aria-label="Attach image, PDF, Word document, audio or video"
            title="Attach files"
          >
            <Icon name="attachment" size={20} />
          </button>
          <button
            type="button"
            className="composer-icon-button mic-button"
            disabled
            aria-label="Voice input unavailable"
            title="Voice input"
          >
            <Icon name="mic" size={18} />
          </button>
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            disabled={disabled}
            rows="1"
            placeholder="Describe today's HCP interaction..."
            aria-label="Natural language CRM message"
          />
          <button
            type="submit"
            className="send-button"
            disabled={disabled || !message.trim()}
            aria-label="Send message"
            title="Send"
          >
            <Icon name="arrowUp" size={20} />
          </button>
        </div>
      </div>
    </form>
  );
}
