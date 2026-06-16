type DataStateProps = {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function LoadingState({ title = "Loading" }: Partial<DataStateProps>) {
  return (
    <div className="state-panel" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <strong>{title}</strong>
    </div>
  );
}

export function EmptyState({ title, description, actionLabel, onAction }: DataStateProps) {
  return (
    <div className="state-panel">
      <strong>{title}</strong>
      <p>{description}</p>
      {actionLabel && onAction ? (
        <button type="button" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}

export function ErrorState({ title, description, actionLabel = "Refresh", onAction }: DataStateProps) {
  return (
    <div className="state-panel error-state" role="alert">
      <strong>{title}</strong>
      <p>{description}</p>
      {onAction ? (
        <button type="button" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
