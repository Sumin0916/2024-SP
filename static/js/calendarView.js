document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',  // 월간 뷰로 시작
        events: '/get-reservations',  // 예약 데이터를 로드할 URL
        // 이벤트 스타일링 및 클릭 핸들러 등 추가 설정 가능
    });
    calendar.render();
});
