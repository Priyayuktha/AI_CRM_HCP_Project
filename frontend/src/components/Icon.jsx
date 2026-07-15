const iconPaths = {
  ai: (
    <>
      <path d="M12 3l1.4 4.1L17.5 8.5l-4.1 1.4L12 14l-1.4-4.1-4.1-1.4 4.1-1.4L12 3Z" />
      <path d="M18 13l.8 2.2L21 16l-2.2.8L18 19l-.8-2.2L15 16l2.2-.8L18 13Z" />
      <path d="M6 14l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7.7-2Z" />
    </>
  ),
  attachment: (
    <path d="M21 11.5 12.2 20.3a6 6 0 0 1-8.5-8.5l9.1-9.1a4 4 0 1 1 5.7 5.7l-9.1 9.1a2 2 0 1 1-2.8-2.8l8.4-8.4" />
  ),
  arrowUp: (
    <>
      <path d="M12 19V5" />
      <path d="m5 12 7-7 7 7" />
    </>
  ),
  plus: (
    <>
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </>
  ),
  doctor: (
    <>
      <path d="M8 3h8v5a4 4 0 0 1-8 0V3Z" />
      <path d="M6 21v-3a6 6 0 0 1 12 0v3" />
      <path d="M12 15v6" />
      <path d="M9 18h6" />
    </>
  ),
  chat: (
    <>
      <path d="M5 5h14v10H8l-3 3V5Z" />
      <path d="M8 9h8" />
      <path d="M8 12h5" />
    </>
  ),
  materials: (
    <>
      <path d="M7 3h8l4 4v14H7V3Z" />
      <path d="M15 3v5h4" />
      <path d="M9 13h6" />
      <path d="M9 17h6" />
    </>
  ),
  heart: (
    <path d="M20.8 8.6c0 5-8.8 10.4-8.8 10.4S3.2 13.6 3.2 8.6A4.4 4.4 0 0 1 11 5.8a4.4 4.4 0 0 1 9.8 2.8Z" />
  ),
  target: (
    <>
      <circle cx="12" cy="12" r="8" />
      <circle cx="12" cy="12" r="4" />
      <path d="M12 8v4l3 2" />
    </>
  ),
  calendar: (
    <>
      <path d="M5 5h14v16H5V5Z" />
      <path d="M8 3v4" />
      <path d="M16 3v4" />
      <path d="M5 10h14" />
    </>
  ),
  summary: (
    <>
      <path d="M6 3h12v18H6V3Z" />
      <path d="M9 8h6" />
      <path d="M9 12h6" />
      <path d="M9 16h4" />
    </>
  ),
  check: (
    <path d="m5 12 4 4L19 6" />
  ),
  file: (
    <>
      <path d="M7 3h7l5 5v13H7V3Z" />
      <path d="M14 3v6h5" />
    </>
  ),
  mic: (
    <>
      <path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3Z" />
      <path d="M5 11a7 7 0 0 0 14 0" />
      <path d="M12 18v3" />
      <path d="M9 21h6" />
    </>
  ),
};

export function Icon({ name, size = 20, className = '', title }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={title ? undefined : 'true'}
      role={title ? 'img' : undefined}
    >
      {title && <title>{title}</title>}
      {iconPaths[name] ?? iconPaths.file}
    </svg>
  );
}
