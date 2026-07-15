import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { resetChatSession, sendChatMessage } from '../services/api';

const assistantWelcome = () => ({
  id: crypto.randomUUID(),
  role: 'assistant',
  content: 'Hi! \uD83D\uDC4B Describe today\'s HCP interaction and I\'ll automatically update the CRM form.',
  timestamp: new Date().toISOString(),
  meta: {
    tool: 'ready',
    status: 'ready',
    history: [],
  },
});

const initialState = {
  messages: [assistantWelcome()],
  currentInteraction: {},
  lastResponse: null,
  lastSubmittedMessage: null,
  loading: false,
  resetLoading: false,
  error: null,
  notification: null,
};

const fieldAliases = {
  doctorName: ['doctor_name', 'doctorName', 'Doctor Name', 'hcp_name', 'hcpName', 'name'],
  hospital: ['hospital', 'Hospital', 'institution', 'clinic'],
  city: ['city', 'City', 'location'],
  specialization: ['specialization', 'Specialization', 'speciality', 'Speciality'],
  interactionDate: ['interaction_date', 'interactionDate', 'Interaction Date', 'date'],
  interactionTime: ['interaction_time', 'interactionTime', 'Interaction Time', 'time', 'Time'],
  interactionType: ['interaction_type', 'interactionType', 'Interaction Type', 'type'],
  attendees: ['attendees', 'Attendees'],
  topicsDiscussed: ['topics_discussed', 'topicsDiscussed', 'Topics Discussed', 'topics'],
  sentiment: ['sentiment', 'Sentiment'],
  materialsShared: ['materials_shared', 'materialsShared', 'Materials Shared', 'materials'],
  samplesDistributed: ['samples_distributed', 'samplesDistributed', 'Samples Distributed', 'samples', 'Samples'],
  outcome: ['outcome', 'Outcome', 'Outcomes', 'outcomes'],
  summary: ['summary', 'Summary'],
  followUpDate: ['follow_up_date', 'followUpDate', 'Follow-up Date', 'Follow Up Date', 'next_follow_up'],
  followUp: ['next_action', 'nextAction', 'Next Action', 'follow_up', 'followUp', 'Follow-up', 'Follow Up'],
  priority: ['priority', 'Priority', 'Follow-up Priority', 'follow_up_priority'],
  status: ['status', 'Status', 'Follow-up Status', 'follow_up_status', 'followUpStatus'],
};

const knownFieldKeys = Object.values(fieldAliases)
  .flat()
  .map((key) => key.toLowerCase());

const getValue = (source, keys) => {
  if (!source || typeof source !== 'object') return '';

  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null && source[key] !== '') {
      return source[key];
    }
  }

  return '';
};

const readableToolName = (tool) =>
  (tool ?? 'crm')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());

const toDisplayString = (value) => {
  if (Array.isArray(value)) return value.filter(Boolean).join(', ');
  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(([key, nestedValue]) => `${readableToolName(key)}: ${toDisplayString(nestedValue)}`)
      .join('; ');
  }
  return value ?? '';
};

const extractPayloadData = (payload = {}) => payload.extracted_data ?? payload.extractedData ?? payload.data ?? {};

const flattenPayloadSource = (payload = {}) => {
  const extracted = extractPayloadData(payload);
  const result = payload.result ?? {};
  const resultFields = { ...result };
  delete resultFields.status;
  delete resultFields.message;
  const hcp = result.hcp ?? payload.hcp ?? {};

  return {
    ...resultFields,
    ...hcp,
    ...extracted,
  };
};

const normalizeKnownFields = (source = {}) => ({
  doctorName: toDisplayString(getValue(source, fieldAliases.doctorName)),
  hospital: toDisplayString(getValue(source, fieldAliases.hospital)),
  city: toDisplayString(getValue(source, fieldAliases.city)),
  specialization: toDisplayString(getValue(source, fieldAliases.specialization)),
  interactionDate: toDisplayString(getValue(source, fieldAliases.interactionDate)),
  interactionTime: toDisplayString(getValue(source, fieldAliases.interactionTime)),
  interactionType: toDisplayString(getValue(source, fieldAliases.interactionType)),
  attendees: toDisplayString(getValue(source, fieldAliases.attendees)),
  topicsDiscussed: toDisplayString(getValue(source, fieldAliases.topicsDiscussed)),
  sentiment: toDisplayString(getValue(source, fieldAliases.sentiment)),
  materialsShared: toDisplayString(getValue(source, fieldAliases.materialsShared)),
  samplesDistributed: toDisplayString(getValue(source, fieldAliases.samplesDistributed)),
  outcome: toDisplayString(getValue(source, fieldAliases.outcome)),
  summary: toDisplayString(getValue(source, fieldAliases.summary)),
  followUpDate: toDisplayString(getValue(source, fieldAliases.followUpDate)),
  followUp: toDisplayString(getValue(source, fieldAliases.followUp)),
  priority: toDisplayString(getValue(source, fieldAliases.priority)),
  status: toDisplayString(getValue(source, fieldAliases.status)),
});

export const normalizeInteraction = (payload = {}) => {
  const merged = flattenPayloadSource(payload);

  return {
    ...normalizeKnownFields(merged),
    additionalFields: Object.fromEntries(
      Object.entries(merged)
        .filter(([key]) => {
          const normalized = key.toLowerCase();
          return !knownFieldKeys.includes(normalized) && normalized !== 'history';
        })
        .map(([key, value]) => [key, toDisplayString(value)]),
    ),
  };
};

const normalizeHistoryItem = (item = {}, extracted = {}) => {
  const merged = { ...extracted, ...item };

  return {
    id: item.id ?? item.interaction_id ?? crypto.randomUUID(),
    ...normalizeKnownFields(merged),
  };
};

const getHistoryItems = (payload = {}) => {
  const extracted = extractPayloadData(payload);
  const history =
    payload.result?.history ??
    payload.history ??
    payload.result?.interactions ??
    payload.interactions ??
    [];

  return Array.isArray(history) ? history.map((item) => normalizeHistoryItem(item, extracted)) : [];
};

const getDoctorProfiles = (payload = {}) => {
  const hcp = payload.result?.hcp ?? payload.hcp;
  const hcps = payload.result?.hcps ?? payload.hcps ?? payload.result?.results ?? payload.results;
  const profiles = Array.isArray(hcps) ? hcps : hcp ? [hcp] : [];

  return profiles.map((profile) => ({
    id: profile.id ?? profile.hcp_id ?? crypto.randomUUID(),
    name: toDisplayString(profile.name ?? profile.doctor_name ?? profile['Doctor Name']),
    hospital: toDisplayString(profile.hospital ?? profile.Hospital),
    city: toDisplayString(profile.city ?? profile.City),
    specialization: toDisplayString(profile.specialization ?? profile.Specialization),
    lastInteractionDate: toDisplayString(profile.last_interaction_date ?? profile.lastInteractionDate),
  }));
};

const getFollowUps = (payload = {}) => {
  const followUps =
    payload.result?.follow_ups ??
    payload.follow_ups ??
    [];

  return Array.isArray(followUps)
    ? followUps.map((followUp) => ({
        id: followUp.id ?? followUp.interaction_id ?? crypto.randomUUID(),
        doctorName: toDisplayString(followUp.doctor_name ?? followUp.doctorName),
        hospital: toDisplayString(followUp.hospital),
        followUpDate: toDisplayString(followUp.follow_up_date ?? followUp.followUpDate),
        priority: toDisplayString(followUp.priority ?? followUp.Priority),
        nextAction: toDisplayString(followUp.next_action ?? followUp.nextAction),
        status: toDisplayString(followUp.status ?? followUp.follow_up_status),
      }))
    : [];
};

const mergeInteraction = (previous = {}, next = {}) => {
  const merged = {
    ...previous,
    additionalFields: {
      ...(previous.additionalFields ?? {}),
    },
  };

  Object.entries(next).forEach(([key, value]) => {
    if (key === 'additionalFields') {
      Object.entries(value ?? {}).forEach(([additionalKey, additionalValue]) => {
        if (additionalValue) merged.additionalFields[additionalKey] = additionalValue;
      });
      return;
    }

    if (value) merged[key] = value;
  });

  return merged;
};

const buildAssistantContent = (payload) => {
  const tool = payload?.tool ?? 'crm';
  const conversationalMessage = payload?.message;

  if (conversationalMessage) return conversationalMessage;
  if (tool === 'interaction_history') {
    return getHistoryItems(payload).length ? 'Interaction history loaded.' : 'No interaction history found.';
  }
  if (tool === 'search_hcp') {
    return getDoctorProfiles(payload).length ? 'Doctor profile loaded.' : 'No matching doctor profile found.';
  }
  if (tool === 'edit_interaction') return '\u2705 Interaction updated successfully.';
  if (tool === 'follow_up_planner') {
    if (payload?.result?.operation === 'list') {
      return getFollowUps(payload).length ? 'Follow-ups loaded.' : 'No upcoming follow-ups found.';
    }
    return '\u2705 Follow-up updated successfully.';
  }
  return '\u2705 Interaction logged successfully. The CRM form has been updated.';
};

const buildAssistantMeta = (payload) => ({
  tool: payload?.tool ?? 'crm',
  status: payload?.result?.status ?? payload?.status ?? 'success',
  history: getHistoryItems(payload),
  followUps: getFollowUps(payload),
  followUpOperation: payload?.result?.operation ?? '',
  extractedFields: normalizeInteraction(payload),
  doctorProfiles: getDoctorProfiles(payload),
});

export const submitChatMessage = createAsyncThunk(
  'chat/submitMessage',
  async (request, { rejectWithValue }) => {
    try {
      const message = typeof request === 'string' ? request : request.message;
      const response = await sendChatMessage(message);

      return {
        ...response,
        originalMessage: typeof request === 'string' ? request : request.originalMessage,
      };
    } catch (error) {
      return rejectWithValue('Something went wrong. Please try again.');
    }
  },
);

export const resetConversation = createAsyncThunk(
  'chat/resetConversation',
  async (_, { rejectWithValue }) => {
    try {
      await resetChatSession();
      return true;
    } catch (error) {
      return rejectWithValue('Something went wrong. Please try again.');
    }
  },
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addUserMessage(state, action) {
      const content =
        typeof action.payload === 'string' ? action.payload : action.payload.content;
      const retrySource =
        typeof action.payload === 'string' ? action.payload : action.payload.retrySource;

      state.messages.push({
        id: crypto.randomUUID(),
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      });
      if (retrySource) state.lastSubmittedMessage = retrySource;
      state.error = null;
      state.notification = null;
    },
    dismissNotification(state) {
      state.notification = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitChatMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitChatMessage.fulfilled, (state, action) => {
        const meta = buildAssistantMeta(action.payload);
        const displayOnly = ['search_hcp', 'interaction_history', 'follow_up_planner'].includes(meta.tool);

        state.loading = false;
        state.lastResponse = action.payload;
        if (!displayOnly) {
          state.currentInteraction = mergeInteraction(
            state.currentInteraction,
            normalizeInteraction(action.payload),
          );
        }
        state.messages.push({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: buildAssistantContent(action.payload),
          meta,
          timestamp: new Date().toISOString(),
        });
        state.notification = null;
      })
      .addCase(submitChatMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.notification = {
          type: 'error',
          message: 'Something went wrong. Please try again.',
        };
      })
      .addCase(resetConversation.pending, (state) => {
        state.resetLoading = true;
      })
      .addCase(resetConversation.fulfilled, (state) => {
        state.messages = [assistantWelcome()];
        state.currentInteraction = {};
        state.lastResponse = null;
        state.lastSubmittedMessage = null;
        state.loading = false;
        state.resetLoading = false;
        state.error = null;
        state.notification = null;
      })
      .addCase(resetConversation.rejected, (state, action) => {
        state.resetLoading = false;
        state.error = action.payload;
        state.notification = {
          type: 'error',
          message: 'Something went wrong. Please try again.',
        };
      });
  },
});

export const {
  addUserMessage,
  dismissNotification,
} = chatSlice.actions;

export default chatSlice.reducer;
