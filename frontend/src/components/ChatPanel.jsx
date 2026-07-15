import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  addUserMessage,
  submitChatMessage,
} from '../redux/chatSlice';
import { ChatInput } from './ChatInput';
import { Icon } from './Icon';
import { MessageBubble } from './MessageBubble';

const loadingSteps = [
  'Analyzing interaction...',
  'Extracting CRM fields...',
  'Updating the HCP record...',
  'Preparing follow-up context...',
];

export function ChatPanel() {
  const dispatch = useDispatch();
  const { messages, loading, lastSubmittedMessage } = useSelector((state) => state.chat);
  const scrollRef = useRef(null);
  const [loadingStep, setLoadingStep] = useState(0);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) {
      setLoadingStep(0);
      return undefined;
    }

    const interval = window.setInterval(() => {
      setLoadingStep((step) => (step + 1) % loadingSteps.length);
      scrollRef.current?.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }, 1100);

    return () => window.clearInterval(interval);
  }, [loading]);

  const handleSubmit = (message, attachments = []) => {
    const isRetry = message.trim().toLowerCase() === 'retry';
    const originalMessage = isRetry && lastSubmittedMessage ? lastSubmittedMessage : message;
    const attachmentNames = attachments.map((file) => file.name).filter(Boolean);
    const visibleMessage = isRetry && lastSubmittedMessage
      ? `Retrying: ${lastSubmittedMessage}`
      : [
          message,
          attachmentNames.length ? `Attachments: ${attachmentNames.join(', ')}` : '',
        ].filter(Boolean).join('\n');

    dispatch(addUserMessage({ content: visibleMessage, retrySource: originalMessage }));
    dispatch(submitChatMessage({
      message: originalMessage,
      originalMessage,
    }));
  };

  return (
    <section className="panel chat-panel" aria-label="AI assistant chat">
      <div className="panel-header chat-header">
        <div className="panel-title-row">
          <span className="panel-title-icon" aria-hidden="true">
            <Icon name="ai" size={20} />
          </span>
          <h2>AI Assistant</h2>
        </div>
      </div>

      <div className="message-list" ref={scrollRef}>
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {loading && (
          <div className="processing-card" aria-label="AI is processing">
            <div className="processing-orbit" aria-hidden="true" />
            <strong>{loadingSteps[loadingStep]}</strong>
          </div>
        )}
      </div>

      <ChatInput disabled={loading} onSubmit={handleSubmit} />
    </section>
  );
}
