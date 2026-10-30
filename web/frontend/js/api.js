/**
 * Smart Rice Cooker - Clean API Client (2026 Edition)
 * Handles backend communication with graceful fallback and user-friendly error notifications.
 */

import { store } from './state.js';
import { showToast } from './components/toast.js';

export async function fetchConfig() {
  try {
    const res = await fetch('/api/config');
    if (!res.ok) throw new Error('ไม่สามารถโหลดข้อมูลการตั้งค่าได้');
    const data = await res.json();
    store.setState({
      configData: { members: data.members || {} },
      serverInfo: data.server_info || store.getState().serverInfo,
      faceSummary: data.face_summary || store.getState().faceSummary
    });
    return data;
  } catch (err) {
    console.error('fetchConfig failed:', err);
    showToast('โหลดข้อมูลล้มเหลว กรุณาตรวจสอบการเชื่อมต่อ', 'error');
    return null;
  }
}

export async function saveConfig(configData) {
  try {
    const res = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configData)
    });
    const result = await res.json();
    if (result.success) {
      store.setState({ configData });
      showToast('บันทึกข้อมูลเรียบร้อยแล้ว', 'success');
      return true;
    }
    throw new Error(result.error || 'บันทึกไม่สำเร็จ');
  } catch (err) {
    showToast(err.message, 'error');
    return false;
  }
}

export async function addMember(id, displayName, voiceGreeting) {
  try {
    const res = await fetch('/api/members/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, display_name: displayName, voice_greeting: voiceGreeting })
    });
    const data = await res.json();
    if (data.success) {
      store.setState({
        configData: { members: data.members },
        currentMemberId: id,
        faceSummary: data.face_summary || store.getState().faceSummary
      });
      showToast(`เพิ่มสมาชิก "${displayName}" เรียบร้อยแล้ว`, 'success');
      return true;
    }
    throw new Error(data.error || 'ไม่สามารถเพิ่มสมาชิกได้');
  } catch (err) {
    showToast(err.message, 'error');
    return false;
  }
}

export async function deleteMember(memberId) {
  try {
    const res = await fetch('/api/members/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ member_id: memberId })
    });
    const data = await res.json();
    if (data.success) {
      const remainingIds = Object.keys(data.members || {});
      store.setState({
        configData: { members: data.members },
        currentMemberId: remainingIds[0] || '',
        faceSummary: data.face_summary || {}
      });
      showToast('ลบสมาชิกเรียบร้อยแล้ว', 'info');
      return true;
    }
    throw new Error(data.error || 'ไม่สามารถลบสมาชิกได้');
  } catch (err) {
    showToast(err.message, 'error');
    return false;
  }
}

export async function fetchMemberFaces(memberId) {
  try {
    const res = await fetch(`/api/member_faces?member_id=${encodeURIComponent(memberId)}`);
    const data = await res.json();
    if (data.success) {
      store.setState({ currentFaceList: data.photos || [] });
      return data.photos || [];
    }
    return [];
  } catch (err) {
    console.error('fetchMemberFaces error:', err);
    return [];
  }
}

export async function deleteFace(memberId, filename) {
  try {
    const res = await fetch('/api/delete_face', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ member_id: memberId, filename })
    });
    const data = await res.json();
    if (data.success) {
      await fetchMemberFaces(memberId);
      // Update summary count
      const summary = { ...store.getState().faceSummary };
      const currentFaces = store.getState().currentFaceList;
      summary[memberId] = {
        count: currentFaces.length,
        latest_url: currentFaces[0] ? currentFaces[0].url : null
      };
      store.setState({ faceSummary: summary });
      showToast('ลบรูปถ่ายใบหน้าเรียบร้อยแล้ว', 'info');
      return true;
    }
    throw new Error(data.error || 'ไม่สามารถลบรูปภาพได้');
  } catch (err) {
    showToast(err.message, 'error');
    return false;
  }
}

export async function uploadFace(memberId, base64Image) {
  try {
    const res = await fetch('/api/upload_face', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ member_id: memberId, image_base64: base64Image })
    });
    const data = await res.json();
    if (data.success) {
      await fetchMemberFaces(memberId);
      showToast('อัปโหลดรูปหน้าใหม่เรียบร้อยแล้ว ระบบกำลังอัปเดตโมเดล AI', 'success');
      return true;
    }
    throw new Error(data.error || 'อัปโหลดรูปภาพล้มเหลว');
  } catch (err) {
    showToast(err.message, 'error');
    return false;
  }
}

export async function captureFaceFromPi(memberId) {
  try {
    const res = await fetch('/api/capture_face', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ member_id: memberId })
    });
    const data = await res.json();
    if (data.success) {
      await fetchMemberFaces(memberId);
      showToast('ถ่ายรูปจากกล้องเครื่องเตือนยาสำเร็จ', 'success');
      return true;
    }
    throw new Error(data.error || 'กล้องไม่ตอบสนอง');
  } catch (err) {
    showToast(err.message, 'error');
    return false;
  }
}

export async function fetchWifiStatus() {
  try {
    const res = await fetch('/api/wifi');
    const data = await res.json();
    store.setState({ wifiStatus: data });
    return data;
  } catch (err) {
    return null;
  }
}

export async function scanWifiNetworks() {
  try {
    const res = await fetch('/api/wifi/scan', { method: 'POST' });
    const data = await res.json();
    return data.networks || [];
  } catch (err) {
    return [];
  }
}

export async function saveWifiNetwork(ssid, password) {
  try {
    const res = await fetch('/api/wifi/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ssid, password })
    });
    const data = await res.json();
    return data;
  } catch (err) {
    return { success: false, message: err.message };
  }
}

export async function fetchAdherence() {
  try {
    const res = await fetch('/api/adherence');
    if (!res.ok) return null;
    const data = await res.json();
    if (data.success && data.adherence) {
      store.setState({ adherence: data.adherence });
      return data.adherence;
    }
  } catch (err) {
    console.error('fetchAdherence error:', err);
  }
  return null;
}

export async function acknowledgeSlot(memberId, slotKey) {
  try {
    const res = await fetch('/api/adherence/ack', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ member_id: memberId, slot_key: slotKey })
    });
    const data = await res.json();
    if (data.success) {
      store.setState({ adherence: data.adherence });
      showToast(data.message || 'บันทึกสถานะเรียบร้อยแล้ว', 'success');
      return data.adherence;
    }
  } catch (err) {
    showToast('เกิดข้อผิดพลาดในการบันทึกสถานะ', 'error');
  }
  return null;
}

export async function resetSlotAdherence(memberId, slotKey) {
  try {
    const res = await fetch('/api/adherence/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ member_id: memberId, slot_key: slotKey })
    });
    const data = await res.json();
    if (data.success) {
      store.setState({ adherence: data.adherence });
      showToast(data.message || 'รีเซ็ตสถานะเรียบร้อยแล้ว', 'info');
      return data.adherence;
    }
  } catch (err) {
    showToast('เกิดข้อผิดพลาดในการรีเซ็ตสถานะ', 'error');
  }
  return null;
}

// --- System & Hardware Controls ---

export async function syncSystemTime(timeStr) {
  try {
    const res = await fetch('/api/system/sync_time', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time_str: timeStr })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || 'ซิงค์เวลากับเครื่องเรียบร้อยแล้ว', 'success');
      return true;
    }
    throw new Error(data.message || 'ไม่สามารถซิงค์เวลาได้');
  } catch (err) {
    showToast(err.message, 'error');
    return false;
  }
}

export async function fetchSystemVolume() {
  try {
    const res = await fetch('/api/system/volume');
    const data = await res.json();
    return data.volume || 80;
  } catch (err) {
    return 80;
  }
}

export async function setSystemVolume(percent) {
  try {
    const res = await fetch('/api/system/volume', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ volume: percent })
    });
    const data = await res.json();
    return data.success;
  } catch (err) {
    return false;
  }
}

export async function testPiSound() {
  try {
    const res = await fetch('/api/system/test_sound', { method: 'POST' });
    const data = await res.json();
    showToast(data.message || 'ทดสอบเสียงลำโพงแล้ว', 'info');
    return data.success;
  } catch (err) {
    showToast('ทดสอบเสียงล้มเหลว', 'error');
    return false;
  }
}

export async function testTelegram() {
  try {
    const res = await fetch('/api/system/test_telegram', { method: 'POST' });
    const data = await res.json();
    showToast(data.message || 'ส่งข้อความทดสอบ Telegram แล้ว', 'success');
    return data.success;
  } catch (err) {
    showToast('ส่งข้อความ Telegram ล้มเหลว', 'error');
    return false;
  }
}

export async function triggerDemoSimulation(scenario, memberId) {
  try {
    const res = await fetch('/api/demo/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario, member_id: memberId })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || 'เริ่มจำลองสถานการณ์แล้ว', 'success');
      return true;
    }
    throw new Error(data.message || 'จำลองสถานการณ์ไม่สำเร็จ');
  } catch (err) {
    showToast(err.message, 'error');
    return false;
  }
}

export async function fetchAdherenceHistory() {
  try {
    const res = await fetch('/api/adherence/history');
    const data = await res.json();
    return data.history || {};
  } catch (err) {
    return {};
  }
}

export async function clearAdherenceHistory() {
  try {
    const res = await fetch('/api/adherence/clear', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast('ล้างประวัติการทานยาเรียบร้อยแล้ว', 'info');
      return true;
    }
  } catch (err) {
    showToast('ล้างประวัติไม่สำเร็จ', 'error');
  }
  return false;
}
