import { api } from './client.js';

export const ivrApi = {
  // 4-step location waterfall resolver diagnostic
  resolveLocation: (callerPhone, dialedNumber = null) => {
    let url = `/api/ivr/resolve-location?caller_phone=${encodeURIComponent(callerPhone)}`;
    if (dialedNumber) url += `&dialed_number=${encodeURIComponent(dialedNumber)}`;
    return api.get(url);
  },

  // Simulate inbound call
  simulateIncomingCall: (callerPhone, dialedNumber, language = 'hi') => 
    api.post('/api/ivr/exotel/incoming-call', {
      From: callerPhone,
      To: dialedNumber,
      language: language
    }),

  // Speech turn for telephone simulator
  sendSpeechTurn: (callSid, speechResult) => 
    api.post('/api/ivr/exotel/speech-turn', {
      CallSid: callSid,
      SpeechResult: speechResult
    }),

  // End call
  endCall: (callSid) => 
    api.post('/api/ivr/exotel/end-call', { CallSid: callSid })
};
