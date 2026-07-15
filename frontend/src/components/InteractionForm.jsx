import { useSelector } from 'react-redux';
const emptyInteraction = {
  doctorName: '',
  hospital: '',
  city: '',
  specialization: '',
  interactionDate: '',
  interactionTime: '',
  interactionType: '',
  attendees: '',
  topicsDiscussed: '',
  sentiment: '',
  materialsShared: '',
  samplesDistributed: '',
  outcome: '',
  summary: '',
  followUpDate: '',
  followUp: '',
  priority: '',
  status: '',
};

const notAvailable = 'Not Available';
const displayValue = (value) => value || notAvailable;

const materialOptions = [
  {
    label: 'Brochure',
    icon: '📄',
    keywords: ['brochure', 'pamphlet', 'leaflet'],
  },
  {
    label: 'Sample Kit',
    icon: '💊',
    keywords: ['sample kit', 'medicine sample', 'medicine samples', 'samples', 'drug sample', 'starter kit'],
  },
  {
    label: 'Prescription',
    icon: '📋',
    keywords: ['prescription', 'prescribed', 'rx', 'script'],
  },
  {
    label: 'Clinical Trial Document',
    icon: '📘',
    keywords: ['clinical trial', 'trial document', 'study document', 'trial protocol'],
  },
];

const sentimentOptions = [
  { label: 'Positive', tone: 'positive', icon: '😊' },
  { label: 'Neutral', tone: 'neutral', icon: '😐' },
  { label: 'Negative', tone: 'negative', icon: '😟' },
];

function DoctorAvatarIcon() {
  return (
    <span className="doctor-avatar-icon" aria-hidden="true">
      <span className="doctor-avatar-head" />
      <span className="doctor-avatar-body" />
    </span>
  );
}

function SectionTitle({ icon, title, avatar }) {
  return (
    <div className="crm-section-title">
      {avatar ? (
        <DoctorAvatarIcon />
      ) : (
        <span className="section-icon" aria-hidden="true">
          {icon}
        </span>
      )}
      <h3>{title}</h3>
    </div>
  );
}

function ReadOnlyField({ label, value, wide }) {
  return (
    <label className={wide ? 'crm-field crm-field-wide' : 'crm-field'}>
      <span>{label}</span>
      <input
        key={displayValue(value)}
        className="crm-input"
        value={displayValue(value)}
        readOnly
        aria-readonly="true"
      />
    </label>
  );
}

function InfoCard({ label, value, icon }) {
  return (
    <article className="info-card">
      <span className="info-card-icon" aria-hidden="true">
        {icon}
      </span>
      <div>
        <span>{label}</span>
        <strong>{displayValue(value)}</strong>
      </div>
    </article>
  );
}

function SentimentCards({ sentiment }) {
  const normalized = String(sentiment || '').toLowerCase();

  return (
    <div className="sentiment-card-grid" aria-label="AI detected sentiment">
      {sentimentOptions.map((option) => {
        const active = normalized.includes(option.tone);
        return (
          <article className={active ? 'sentiment-card active' : 'sentiment-card'} key={option.label}>
            <span className="sentiment-emoji" aria-hidden="true">{option.icon}</span>
            <strong>{option.label}</strong>
          </article>
        );
      })}
    </div>
  );
}

function MaterialChips({ interaction }) {
  const combined = [
    interaction.materialsShared,
    interaction.samplesDistributed,
    interaction.summary,
    interaction.outcome,
    interaction.topicsDiscussed,
  ].filter(Boolean).join(' ').toLowerCase();

  return (
    <div className="material-chip-grid">
      {materialOptions.map((material) => {
        const active = material.keywords.some((term) => combined.includes(term.toLowerCase()));
        return (
          <article className={active ? 'material-card active' : 'material-card'} key={material.label}>
            <span className="material-card-icon" aria-hidden="true">{material.icon}</span>
            <span>{material.label}</span>
          </article>
        );
      })}
    </div>
  );
}

function OutcomeField({ outcome }) {
  return (
    <textarea
      key={outcome || notAvailable}
      className="crm-textarea outcome-textarea"
      value={outcome || ''}
      placeholder={notAvailable}
      readOnly
      aria-readonly="true"
      aria-label="Interaction outcome"
    />
  );
}

export function InteractionForm() {
  const currentInteraction = useSelector((state) => state.chat.currentInteraction);
  const interaction = { ...emptyInteraction, ...currentInteraction };

  return (
    <section className="panel form-panel crm-form-panel" aria-label="AI-controlled HCP interaction form">
      <div className="panel-header crm-form-header">
        <div className="panel-title-row">
          <span className="panel-title-icon" aria-hidden="true">
            📋
          </span>
          <div>
            <h2>Log HCP Interaction Form</h2>
            <p>AI-generated CRM form</p>
          </div>
        </div>
      </div>

      <div className="crm-form-sections">
        <section className="crm-form-section">
          <SectionTitle title="Interaction Details" avatar />
          <div className="crm-fields-grid">
            <ReadOnlyField label="HCP Name" value={interaction.doctorName} />
            <ReadOnlyField label="Interaction Type" value={interaction.interactionType} />
            <ReadOnlyField label="Date" value={interaction.interactionDate} />
            <ReadOnlyField label="Time" value={interaction.interactionTime} />
            <ReadOnlyField label="Hospital" value={interaction.hospital} />
            <ReadOnlyField label="City" value={interaction.city} />
            <ReadOnlyField label="Specialization" value={interaction.specialization} />
            <ReadOnlyField label="Attendees" value={interaction.attendees} />
          </div>
        </section>

        <section className="crm-form-section">
          <SectionTitle icon="💬" title="Topics Discussed" />
          <div className="summary-card" key={interaction.topicsDiscussed || notAvailable}>
            {displayValue(interaction.topicsDiscussed)}
          </div>
        </section>

        <section className="crm-form-section">
          <SectionTitle icon="💊" title="Materials Shared" />
          <MaterialChips interaction={interaction} />
        </section>

        <section className="crm-form-section">
          <SectionTitle icon="😊" title="Observed / Inferred Sentiment" />
          <SentimentCards sentiment={interaction.sentiment} />
        </section>

        <section className="crm-form-section">
          <SectionTitle icon="📋" title="Outcomes" />
          <OutcomeField outcome={interaction.outcome} />
        </section>

        <section className="crm-form-section">
          <SectionTitle icon="📅" title="Follow-up" />
          <div className="follow-up-card-grid">
            <InfoCard label="Date" value={interaction.followUpDate} icon="📅" />
            <InfoCard label="Priority" value={interaction.priority} icon="⚡" />
            <InfoCard label="Next Action" value={interaction.followUp} icon="📞" />
            <InfoCard label="Status" value={interaction.status} icon="📌" />
          </div>
        </section>

        <section className="crm-form-section">
          <SectionTitle icon="📝" title="Summary" />
          <div className="summary-card summary-card-large" key={interaction.summary || notAvailable}>
            {displayValue(interaction.summary)}
          </div>
        </section>
      </div>
    </section>
  );
}
