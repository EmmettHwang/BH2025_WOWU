import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// 전역 변수
let aesongScene, aesongCamera, aesongRenderer, aesongModel, aesongAnimationId, aesongMixer;
let isRecording = false;
let recognition = null;
let synthesis = window.speechSynthesis;
let currentCharacter = 'aesong'; // 기본 캐릭터 (예진이)
let currentCharacterName = '예진이'; // 현재 캐릭터 이름
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };
let userRotation = { x: 0, y: 0, z: 0 }; // 사용자가 설정한 회전 값 저장

// Three.js 3D 씬 초기화
export function initAesong3DScene() {
    const container = document.getElementById('aesong-3d-container');
    const canvas = document.getElementById('aesong-canvas');
    
    if (!canvas) {
        console.error('Canvas not found!');
        return;
    }
    
    console.log('🎨 3D 씬 초기화 시작...');
    
    // Three.js 씬 설정
    aesongScene = new THREE.Scene();
    aesongScene.background = new THREE.Color(0x667eea);
    
    // 카메라 설정 (정면에서 보기)
    aesongCamera = new THREE.PerspectiveCamera(
        50,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    aesongCamera.position.set(0, 0.5, 2.5); // 정면 중앙에서 보기
    aesongCamera.lookAt(0, 0, 0); // 원점을 바라보기
    
    // 렌더러 설정
    aesongRenderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
    aesongRenderer.setSize(container.clientWidth, container.clientHeight);
    aesongRenderer.setPixelRatio(window.devicePixelRatio);
    aesongRenderer.shadowMap.enabled = true;
    
    // 조명 설정
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    aesongScene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    directionalLight.castShadow = true;
    aesongScene.add(directionalLight);
    
    const pointLight1 = new THREE.PointLight(0xff69b4, 1, 100);
    pointLight1.position.set(-3, 3, 3);
    aesongScene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight(0x87ceeb, 1, 100);
    pointLight2.position.set(3, 3, -3);
    aesongScene.add(pointLight2);
    
    // 초기 캐릭터 로드
    loadCharacter(currentCharacter);
    
    // 마우스 컨트롤
    canvas.addEventListener('mousedown', () => { isDragging = true; });
    canvas.addEventListener('mouseup', () => { isDragging = false; });
    canvas.addEventListener('mouseleave', () => { isDragging = false; });
    
    canvas.addEventListener('mousemove', (e) => {
        if (isDragging && aesongModel) {
            const deltaX = e.offsetX - previousMousePosition.x;
            const deltaY = e.offsetY - previousMousePosition.y;
            
            // 좌우 회전 (Y축)
            userRotation.y += deltaX * 0.01;
            
            // 상하 회전 (X축)
            userRotation.x += deltaY * 0.01;
            
            // X축 회전 제한 (-1 ~ 1 라디안, 약 ±57도)
            userRotation.x = Math.max(-1, Math.min(1, userRotation.x));
        }
        previousMousePosition = { x: e.offsetX, y: e.offsetY };
    });
    
    // 애니메이션 루프
    const clock = new THREE.Clock();
    function animate() {
        aesongAnimationId = requestAnimationFrame(animate);
        
        const delta = clock.getDelta();
        
        // 애니메이션 믹서 업데이트
        if (aesongMixer) {
            aesongMixer.update(delta);
        }
        
        // 자연스러운 대화 동작 (사용자 회전 + 자연스러운 움직임)
        if (aesongModel) {
            const time = Date.now() * 0.001; // 시간 기반 애니메이션
            
            // 사용자가 설정한 회전 + 자연스러운 미세 움직임
            // 좌우 고개 움직임 (±5도 범위로 축소)
            const naturalYaw = Math.sin(time * 0.5) * 0.08;
            
            // 위아래 고개 끄덕임 (±3도)
            const naturalPitch = Math.sin(time * 0.7) * 0.05;
            
            // 상하 위치 움직임 (호흡하는 느낌, ±0.02 단위)
            const naturalBob = Math.sin(time * 0.6) * 0.02;
            
            // 좌우 기울임 (±2도)
            const naturalRoll = Math.sin(time * 0.3) * 0.03;
            
            // 최종 회전 적용 (사용자 회전 + 자연스러운 움직임)
            aesongModel.rotation.y = userRotation.y + naturalYaw;
            aesongModel.rotation.x = userRotation.x + naturalPitch;
            aesongModel.rotation.z = userRotation.z + naturalRoll;
            
            // 상하 위치 변화 (호흡 효과)
            if (aesongModel.userData.originalY !== undefined) {
                aesongModel.position.y = aesongModel.userData.originalY + naturalBob;
            }
        }
        
        aesongRenderer.render(aesongScene, aesongCamera);
    }
    animate();
    
    // 리사이즈 핸들러
    function onWindowResize() {
        if (aesongCamera && aesongRenderer && container) {
            aesongCamera.aspect = container.clientWidth / container.clientHeight;
            aesongCamera.updateProjectionMatrix();
            aesongRenderer.setSize(container.clientWidth, container.clientHeight);
        }
    }
    window.addEventListener('resize', onWindowResize);
    
    // 음성 인식 초기화
    initSpeechRecognition();
}

// 음성 인식 초기화
function initSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        updateStatusText('이 브라우저는 음성 인식을 지원하지 않습니다');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'ko-KR';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onresult = async function(event) {
        const transcript = event.results[0][0].transcript;
        console.log('인식된 텍스트:', transcript);
        
        // 받침 있으면 '이', 없으면 '가'
        const lastChar = currentCharacterName.charAt(currentCharacterName.length - 1);
        const hasJongseong = (lastChar.charCodeAt(0) - 0xAC00) % 28 > 0;
        const particle = hasJongseong ? '이' : '가';
        updateStatusText(`${currentCharacterName}${particle} 생각 중...`);
        
        // 서버에 메시지 전송
        try {
            const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000';
            // 선택된 AI 모델 가져오기 (localStorage에서)
            const selectedModel = localStorage.getItem('ai_model') || 'groq';
            
            const response = await fetch(`${API_BASE_URL}/api/aesong-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: transcript,
                    character: currentCharacterName, // 캐릭터 이름 전달
                    model: selectedModel // 선택된 AI 모델 전달
                })
            });
            
            const data = await response.json();
            const aiResponse = data.response;
            
            console.log(`${currentCharacterName}: ${aiResponse}`);
            
            // TTS로 음성 출력
            speakText(aiResponse);
            
        } catch (error) {
            console.error('채팅 오류:', error);
            // 받침 있으면 '과', 없으면 '와'
            const lastChar = currentCharacterName.charAt(currentCharacterName.length - 1);
            const hasJongseong = (lastChar.charCodeAt(0) - 0xAC00) % 28 > 0;
            const particle = hasJongseong ? '과' : '와';
            updateStatusText(`${currentCharacterName}${particle} 연결할 수 없어요`);
            speakText(`죄송해요, 지금은 대답하기 어려워요`);
        }
    };
    
    recognition.onerror = function(event) {
        console.error('음성 인식 오류:', event.error);
        updateStatusText('음성 인식 오류: ' + event.error);
        isRecording = false;
        const btn = document.getElementById('voice-btn');
        if (btn) btn.classList.remove('recording');
    };
    
    recognition.onend = function() {
        isRecording = false;
        const btn = document.getElementById('voice-btn');
        if (btn) btn.classList.remove('recording');
        const statusText = document.getElementById('status-text');
        if (statusText && statusText.textContent.includes('말씀하세요')) {
            updateStatusText('마이크 버튼을 눌러서 말해보세요');
        }
    };
}

// 음성 녹음 토글
export function toggleVoiceRecording() {
    if (!recognition) {
        if (window.showAlert) {
            window.showAlert('음성 인식이 지원되지 않습니다', 'error');
        } else {
            alert('음성 인식이 지원되지 않습니다');
        }
        return;
    }
    
    const btn = document.getElementById('voice-btn');
    
    if (isRecording) {
        recognition.stop();
        isRecording = false;
        if (btn) btn.classList.remove('recording');
        updateStatusText('녹음 중지');
    } else {
        recognition.start();
        isRecording = true;
        if (btn) btn.classList.add('recording');
        updateStatusText('말씀하세요...');
    }
}

// TTS 음성 출력 (Google Cloud TTS API 사용)
async function speakText(text) {
    try {
        // 말하는 중 상태 표시
        const lastChar = currentCharacterName.charAt(currentCharacterName.length - 1);
        const hasJongseong = (lastChar.charCodeAt(0) - 0xAC00) % 28 > 0;
        const particle = hasJongseong ? '이' : '가';
        updateStatusText(`${currentCharacterName}${particle} 말하는 중...`);
        
        // Google TTS API 호출
        const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${API_BASE_URL}/api/tts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                character: currentCharacterName
            })
        });
        
        if (!response.ok) {
            throw new Error('TTS API 호출 실패');
        }
        
        const data = await response.json();
        const audioContent = data.audioContent;
        
        console.log(`${currentCharacterName} Google TTS 음성 생성 완료: ${data.voice}`);
        
        // Base64 디코딩 및 오디오 재생
        const audioBlob = base64ToBlob(audioContent, 'audio/mp3');
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        // 오디오가 완전히 로드될 때까지 대기
        audio.preload = 'auto';
        
        audio.onplay = function() {
            console.log(`${currentCharacterName} 음성 재생 시작`);
        };
        
        audio.onended = function() {
            console.log(`${currentCharacterName} 음성 재생 완료`);
            updateStatusText('마이크 버튼을 눌러서 말해보세요');
            URL.revokeObjectURL(audioUrl); // 메모리 해제
        };
        
        audio.onerror = function() {
            console.error('오디오 재생 오류');
            updateStatusText('마이크 버튼을 눌러서 말해보세요');
        };
        
        // 오디오가 충분히 로드된 후 즉시 재생
        audio.oncanplaythrough = async function() {
            try {
                await audio.play();
            } catch (e) {
                console.error('재생 실패:', e);
            }
        };
        
        audio.load();
        
    } catch (error) {
        console.error('TTS 오류:', error);
        updateStatusText('마이크 버튼을 눌러서 말해보세요');
    }
}

// Base64를 Blob으로 변환
function base64ToBlob(base64, mimeType) {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
}

// 상태 텍스트 업데이트
function updateStatusText(text) {
    const statusElement = document.getElementById('status-text');
    if (statusElement) {
        statusElement.textContent = text;
        
        // 로딩 중이거나 생각 중일 때만 표시
        if (text.includes('로딩') || text.includes('생각') || text.includes('말하는')) {
            statusElement.style.display = 'flex';
        } else {
            statusElement.style.display = 'none';
        }
    }
}

// 채팅 메시지 추가 (대화창 제거로 비활성화)
function addChatMessage(sender, message) {
    // 콘솔에만 로그 출력
    console.log(`${sender}: ${message}`);
}

// 캐릭터 로드 함수
function loadCharacter(characterType) {
    // 기존 모델 완전히 제거
    if (aesongModel) {
        // 애니메이션 중지
        if (aesongMixer) {
            aesongMixer.stopAllAction();
            aesongMixer = null;
        }
        
        // 씬에서 제거
        aesongScene.remove(aesongModel);
        
        // 메모리 해제
        aesongModel.traverse((child) => {
            if (child.geometry) child.geometry.dispose();
            if (child.material) {
                if (Array.isArray(child.material)) {
                    child.material.forEach(material => material.dispose());
                } else {
                    child.material.dispose();
                }
            }
        });
        
        aesongModel = null;
    }
    
    currentCharacter = characterType;
    const loader = new GLTFLoader();
    
    let modelPath = '';
    let modelName = '';
    let scale = 1.0;
    let positionY = 0;
    
    if (characterType === 'aesong') {
        modelPath = '/AEsong.glb';
        modelName = '예진이';
        scale = 1.5; // 적당한 크기
        positionY = -0.2; // 가운데 위치
    } else if (characterType === 'david') {
        modelPath = '/David.glb';
        modelName = '데이빗';
        scale = 1.5; // 적당한 크기
        positionY = -0.8; // 키가 크니까 아래로 (얼굴이 보이도록)
    } else if (characterType === 'asol') {
        modelPath = '/pmjung.glb';
        modelName = 'PM 정운표';
        scale = 1.5; // 적당한 크기
        positionY = -0.8; // 성인 남성 키
    } else {
        console.error('알 수 없는 캐릭터 타입:', characterType);
        return;
    }
    
    // 현재 캐릭터 이름 저장
    currentCharacterName = modelName;
    
    updateStatusText(`${modelName} 로딩 중...`);
    
    loader.load(
        modelPath,
        function(gltf) {
            aesongModel = gltf.scene;
            aesongModel.position.set(0, positionY, 0);
            aesongModel.scale.set(scale, scale, scale);
            
            // 원래 Y 위치 저장 (상하 움직임용)
            aesongModel.userData.originalY = positionY;
            
            // 사용자 회전 초기화
            userRotation = { x: 0, y: 0, z: 0 };
            
            // 데이빗은 정면을 보도록 머리를 위로 살짝 들어 올림
            if (characterType === 'david') {
                userRotation.x = -0.2; // 머리를 위로 (음수값 = 위로)
            }
            
            aesongScene.add(aesongModel);
            
            console.log(`${modelName} 3D 모델 로드 완료!`);
            updateStatusText(`${modelName} 준비 완료`);
            
            // 애니메이션 설정
            if (gltf.animations && gltf.animations.length > 0) {
                aesongMixer = new THREE.AnimationMixer(aesongModel);
                gltf.animations.forEach((clip) => {
                    const action = aesongMixer.clipAction(clip);
                    action.play();
                });
                console.log(`🎬 ${modelName} 애니메이션 ${gltf.animations.length}개 재생 중`);
            }
        },
        function(xhr) {
            console.log(`${modelName} 로딩 중...`);
            updateStatusText(`${modelName} 로딩 중...`);
        },
        function(error) {
            console.error(`${modelName} 모델 로드 실패:`, error);
            updateStatusText(`${modelName}를 불러오는데 실패했습니다`);
        }
    );
}

// 캐릭터 전환 함수
export function switchCharacter(characterType) {
    console.log('캐릭터 전환:', characterType);
    
    // UI 업데이트
    document.querySelectorAll('.character-option').forEach(option => {
        option.classList.remove('active');
    });
    document.querySelector(`[data-character="${characterType}"]`).classList.add('active');
    
    // 캐릭터 로드
    loadCharacter(characterType);
}

// 전역에 함수 노출
window.initAesong3DScene = initAesong3DScene;
window.toggleVoiceRecording = toggleVoiceRecording;
window.switchCharacter = switchCharacter;
