import { useDispatch, useSelector } from 'react-redux';
import {
  addUserMessage,
  dismissNotification,
  submitChatMessage,
} from '../redux/chatSlice';

export function Notification() {
  const dispatch = useDispatch();
  const { notification, lastSubmittedMessage, loading } = useSelector((state) => state.chat);

  const visibleMessage = notification;

  if (!visibleMessage) return null;

  const handleRetry = () => {
    if (!lastSubmittedMessage || loading) return;

    dispatch(addUserMessage({ content: `Retrying: ${lastSubmittedMessage}`, retrySource: lastSubmittedMessage }));
    dispatch(submitChatMessage({
      message: lastSubmittedMessage,
      originalMessage: lastSubmittedMessage,
    }));
  };

  return (
    <div className={`toast notification-${visibleMessage.type}`} role="status" aria-live="polite">
      <span>{visibleMessage.message}</span>
      <div className="notification-actions">
        {visibleMessage.type === 'error' && (
          <button type="button" className="retry-button" onClick={handleRetry} disabled={!lastSubmittedMessage || loading}>
            Retry
          </button>
        )}
        <button type="button" onClick={() => dispatch(dismissNotification())} aria-label="Dismiss">
          x
        </button>
      </div>
    </div>
  );
}
