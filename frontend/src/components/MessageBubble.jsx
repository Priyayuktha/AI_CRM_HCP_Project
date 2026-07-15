const formatTime = (timestamp) =>
  new Intl.DateTimeFormat('en', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(timestamp));

const fallback = (value) => value || 'Not Available';

const formatDisplayDate = (value) => {
  if (!value) return 'Not Available';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat('en', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(parsed);
};

function HistoryTimeline({ history }) {
  if (!history?.length) return null;

  return (
    <div className="history-timeline" aria-label="Interaction history">
      {history.map((interaction) => (
        <article className="history-card" key={interaction.id}>
          <div className="timeline-marker" aria-hidden="true" />
          <div className="history-card-body">
            <div className="history-card-header">
              <div>
                <h3>{fallback(interaction.interactionType)}</h3>
                <p>{fallback(interaction.doctorName)}</p>
              </div>
              <span>{formatDisplayDate(interaction.interactionDate)}</span>
            </div>

            <div className="history-meta-grid">
              <div>
                <span>Sentiment</span>
                <strong>{fallback(interaction.sentiment)}</strong>
              </div>
              <div>
                <span>Materials Shared</span>
                <strong>{fallback(interaction.materialsShared)}</strong>
              </div>
            </div>

            <dl className="history-details">
              <div>
                <dt>Summary</dt>
                <dd>{fallback(interaction.summary)}</dd>
              </div>
            </dl>
          </div>
        </article>
      ))}
    </div>
  );
}

function DoctorProfileCards({ profiles }) {
  if (!profiles?.length) return null;

  return (
    <div className="doctor-profile-list" aria-label="Doctor search results">
      {profiles.map((profile) => (
        <article className="doctor-profile-card" key={profile.id}>
          <div className="doctor-avatar" aria-hidden="true">
            {profile.name ? profile.name.slice(0, 2).toUpperCase() : 'DR'}
          </div>
          <div className="doctor-profile-main">
            <div className="doctor-profile-header">
              <div>
                <span>Doctor Profile</span>
                <h3>{fallback(profile.name)}</h3>
              </div>
              <strong>{fallback(profile.specialization)}</strong>
            </div>
            <div className="doctor-profile-grid">
              <div>
                <span>Hospital</span>
                <strong>{fallback(profile.hospital)}</strong>
              </div>
              <div>
                <span>Specialization</span>
                <strong>{fallback(profile.specialization)}</strong>
              </div>
              <div>
                <span>City</span>
                <strong>{fallback(profile.city)}</strong>
              </div>
              <div>
                <span>Last Interaction Date</span>
                <strong>{formatDisplayDate(profile.lastInteractionDate)}</strong>
              </div>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

function FollowUpCards({ followUps }) {
  if (!followUps?.length) return null;

  return (
    <div className="follow-up-result-list" aria-label="Upcoming follow-ups">
      {followUps.map((followUp) => (
        <article className="follow-up-result-card" key={followUp.id}>
          <div>
            <span>Doctor Name</span>
            <strong>{fallback(followUp.doctorName)}</strong>
          </div>
          <div>
            <span>Follow-up Date</span>
            <strong>{formatDisplayDate(followUp.followUpDate)}</strong>
          </div>
          <div>
            <span>Priority</span>
            <strong>{fallback(followUp.priority)}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong>{fallback(followUp.status)}</strong>
          </div>
          <div>
            <span>Next Action</span>
            <strong>{fallback(followUp.nextAction)}</strong>
          </div>
        </article>
      ))}
    </div>
  );
}

export function MessageBubble({ message }) {
  const meta = message.meta ?? {};
  const showDoctorProfiles =
    message.role === 'assistant' && meta.tool === 'search_hcp' && meta.doctorProfiles?.length;
  const showHistory =
    message.role === 'assistant' && meta.tool === 'interaction_history' && meta.history?.length;
  const showFollowUps =
    message.role === 'assistant' &&
    meta.tool === 'follow_up_planner' &&
    meta.followUpOperation === 'list' &&
    meta.followUps?.length;
  const showCards = showDoctorProfiles || showHistory || showFollowUps;

  return (
    <article className={`message-bubble ${message.role} ${message.isError ? 'error' : ''}`}>
      <div className="message-content">
        {!showCards && message.content.split('\n').map((line, index) => (
          <p key={`${message.id}-${index}`}>{line || '\u00A0'}</p>
        ))}
        {showDoctorProfiles && <DoctorProfileCards profiles={meta.doctorProfiles} />}
        {showHistory && <HistoryTimeline history={meta.history} />}
        {showFollowUps && <FollowUpCards followUps={meta.followUps} />}
      </div>
      {!showCards && <time dateTime={message.timestamp}>{formatTime(message.timestamp)}</time>}
    </article>
  );
}
