export function LoadingSpinner({ label = 'Processing' }) {
  return (
    <div className="loading-spinner" role="status" aria-live="polite">
      <span aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
