<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard | Retouch E-Bid</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Sarabun:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --secondary: #ec4899;
            --background: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Outfit', 'Sarabun', sans-serif;
            background-color: var(--background);
            color: var(--text-main);
            min-height: 100vh;
            padding: 40px 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
        }

        h1 {
            font-size: 2.5rem;
            background: linear-gradient(to right, #818cf8, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 20px;
            text-align: center;
        }

        .stat-card h3 {
            font-size: 2rem;
            color: var(--primary);
            margin-bottom: 5px;
        }

        .stat-card p {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .jobs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 24px;
        }

        .job-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 24px;
            overflow: hidden;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }

        .job-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
        }

        .job-img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-bottom: 1px solid var(--border);
        }

        .job-body {
            padding: 24px;
        }

        .job-desc {
            font-size: 1rem;
            margin-bottom: 15px;
            color: var(--text-main);
            height: 3rem;
            overflow: hidden;
        }

        .job-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .budget {
            font-size: 1.25rem;
            font-weight: 700;
            color: #fbbf24;
        }

        .time {
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .actions {
            display: flex;
            gap: 12px;
        }

        .btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
        }

        .btn-reply {
            background: var(--primary);
            color: white;
        }

        .btn-reply:hover {
            background: var(--primary-hover);
        }

        .btn-cancel {
            background: #ef4444;
            color: white;
        }

        .btn-cancel:hover {
            background: #dc2626;
        }

        .warning-box {
            background: #450a0a;
            border: 1px solid #991b1b;
            color: #fecaca;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 30px;
            font-size: 0.9rem;
        }

        /* Chat Modal */
        .modal {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal-content {
            background: var(--card-bg);
            width: 100%;
            max-width: 500px;
            padding: 32px;
            border-radius: 24px;
            border: 1px solid var(--border);
        }

        textarea {
            width: 100%;
            background: #0f172a;
            border: 1px solid var(--border);
            color: white;
            padding: 15px;
            border-radius: 12px;
            margin: 15px 0;
            font-family: inherit;
        }

        .alert {
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: none;
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="warning-box">
            <strong>ADMIN MODE:</strong> ไฟล์นี้ใช้งานในเครื่องเท่านั้น ห้ามแชร์ URL หรือไฟล์นี้ให้ผู้อื่น
        </div>

        <div class="header">
            <h1>Dashboard</h1>
            <div>
                <button class="btn btn-reply" style="padding: 12px 24px;" onclick="location.reload()">Refresh</button>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3 id="statTotal">0</h3>
                <p>งานทั้งหมด</p>
            </div>
            <div class="stat-card">
                <h3 id="statActive">0</h3>
                <p>กำลังรอ/ดำเนินการ</p>
            </div>
        </div>

        <div id="jobsContainer" class="jobs-grid">
            <p>Loading tasks...</p>
        </div>
    </div>

    <!-- Reply Modal -->
    <div id="replyModal" class="modal">
        <div class="modal-content">
            <h3>ตอบรับงาน</h3>
            <p id="replyJobId" style="font-size: 0.8rem; color: var(--text-muted);"></p>
            <textarea id="replyText" rows="4" placeholder="พิมพ์ข้อความตอบกลับเพื่อรับงาน..."></textarea>
            <div class="actions">
                <button class="btn" style="background: #334155; color: white;" onclick="closeModal()">ยกเลิก</button>
                <button class="btn btn-reply" onclick="sendReply()">ส่งและรับงาน</button>
            </div>
        </div>
    </div>

    <script type="module">
        // ============================================
        // FIREBASE CONFIGURATION - ต้องแก้ไขที่นี่ก่อนใช้งาน
        // ดูวิธีตั้งค่าในไฟล์ README-SETUP-FIREBASE.md
        // ให้ใช้ config เดียวกับ index.html
        // ============================================
        import { initializeApp } from "https://www.gstatic.com/firebasejs/12.12.1/firebase-app.js";
        import { getDatabase, ref, onValue, update, push, set } from "https://www.gstatic.com/firebasejs/12.12.1/firebase-database.js";

        const firebaseConfig = {
            apiKey: "AIzaSyDWzE4nEYt6fWPS2q6KscvoBbYxL_tdRzk",
            authDomain: "retouch-ebid.firebaseapp.com",
            databaseURL: "https://retouch-ebid-default-rtdb.asia-southeast1.firebasedatabase.app",
            projectId: "retouch-ebid",
            storageBucket: "retouch-ebid.firebasestorage.app",
            messagingSenderId: "1016195918066",
            appId: "1:1016195918066:web:b623d84af8aa4920ba886b"
        };

        const app = initializeApp(firebaseConfig);
        const database = getDatabase(app);
        const jobsRef = ref(database, 'jobs');
        const chatsRef = ref(database, 'chats');

        let currentJobId = null;
        let currentJobFirebaseKey = null;

        onValue(jobsRef, (snapshot) => {
            const container = document.getElementById('jobsContainer');
            if (!snapshot.exists()) {
                container.innerHTML = '<p>No jobs found.</p>';
                return;
            }

            const jobs = snapshot.val();
            const jobEntries = Object.entries(jobs);
            
            document.getElementById('statTotal').textContent = jobEntries.length;
            document.getElementById('statActive').textContent = jobEntries.filter(([k,v]) => v.status === 'active').length;

            container.innerHTML = jobEntries.reverse().map(([key, job]) => {
                const now = new Date();
                const expired = new Date(job.expiresAt) < now;
                if (expired && job.status === 'active') {
                    // Optionally update status to expired in DB
                }

                return `
                    <div class="job-card" style="${job.status !== 'active' ? 'opacity: 0.5' : ''}">
                        <img src="${job.imageUrl}" class="job-img">
                        <div class="job-body">
                            <div class="job-desc">${job.description}</div>
                            <div class="job-meta">
                                <div class="budget">฿${job.budget}</div>
                                <div class="time">${new Date(job.createdAt).toLocaleTimeString()}</div>
                            </div>
                            <div class="actions">
                                ${job.status === 'active' ? `
                                    <button class="btn btn-reply" onclick="openReply('${key}', '${job.uniqueId}')">รับงาน/ตอบกลับ</button>
                                    <button class="btn btn-cancel" onclick="cancelJob('${key}')">ยกเลิก</button>
                                ` : `
                                    <button class="btn" disabled>${job.status.toUpperCase()}</button>
                                `}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        });

        window.openReply = (firebaseKey, uniqueId) => {
            currentJobFirebaseKey = firebaseKey;
            currentJobId = uniqueId;
            document.getElementById('replyJobId').textContent = 'Job ID: ' + uniqueId;
            document.getElementById('replyModal').style.display = 'flex';
        };

        window.closeModal = () => {
            document.getElementById('replyModal').style.display = 'none';
        };

        window.sendReply = async () => {
            const text = document.getElementById('replyText').value;
            if (!text) return;

            try {
                // Add message to chat
                const chatRef = ref(database, `chats/${currentJobId}`);
                await push(chatRef, {
                    sender: 'admin',
                    text: text,
                    timestamp: new Date().toISOString()
                });

                // Update job status if needed, or just let the chat presence signify progress
                // The index.html checks if the chat node exists.
                
                alert('ส่งข้อความสำเร็จ! งานนี้จะขึ้นสถานะ "กำลังดำเนินงาน" ในหน้าหลัก');
                closeModal();
                document.getElementById('replyText').value = '';
            } catch (error) {
                console.error(error);
                alert('Error sending reply');
            }
        };

        window.cancelJob = async (key) => {
            if (confirm('ยืนยันการยกเลิกงาน?')) {
                const jobRef = ref(database, `jobs/${key}`);
                await update(jobRef, { status: 'cancelled' });
            }
        };

        window.openReply = openReply;
        window.closeModal = closeModal;
        window.sendReply = sendReply;
        window.cancelJob = cancelJob;
    </script>
</body>
</html>
                                                                                                                                                                                                                                                                                                                                                                                                          