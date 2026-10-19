/**
 * Smart Rice Cooker - Reactive State Store (2026 Edition)
 * Single Source of Truth for configuration, members, face datasets, and device connectivity.
 */

class StateStore {
  constructor() {
    this.state = {
      configData: { members: {} },
      currentMemberId: '',
      serverInfo: {
        local_ip: '127.0.0.1',
        port: 8080,
        mobile_url: '',
        pi_ip: ''
      },
      faceSummary: {},
      currentFaceList: [],
      wifiStatus: {
        current: '',
        saved: [],
        pi_ip: ''
      },
      deferredInstallPrompt: null
    };

    this.listeners = new Set();
  }

  getState() {
    return this.state;
  }

  setState(partialState) {
    const prevState = { ...this.state };
    this.state = { ...this.state, ...partialState };
    this._notify(prevState);
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  _notify(prevState) {
    for (const listener of this.listeners) {
      try {
        listener(this.state, prevState);
      } catch (err) {
        console.error('State listener error:', err);
      }
    }
  }

  // --- Convenience Getters & Setters ---

  getCurrentMember() {
    const { configData, currentMemberId } = this.state;
    if (!currentMemberId || !configData.members) return null;
    return configData.members[currentMemberId] || null;
  }

  selectMember(memberId) {
    if (this.state.configData.members && this.state.configData.members[memberId]) {
      this.setState({ currentMemberId: memberId });
    }
  }

  setEmbeddedData(embedded) {
    if (!embedded) return;
    const configData = { members: embedded.config?.members || {} };
    const memberIds = Object.keys(configData.members);
    const currentMemberId = this.state.currentMemberId && configData.members[this.state.currentMemberId]
      ? this.state.currentMemberId
      : (memberIds[0] || '');

    this.setState({
      configData,
      currentMemberId,
      serverInfo: embedded.server_info || this.state.serverInfo,
      faceSummary: embedded.face_summary || this.state.faceSummary
    });
  }
}

export const store = new StateStore();
