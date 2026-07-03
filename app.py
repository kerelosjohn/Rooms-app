import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="نظام تسكين الغرف", layout="wide")

# إعداد الغرف الافتراضية
if "hotel_rooms" not in st.session_state:
    default_rooms = []
    default_rooms.append({"id": "غرفة 1 (سعة 8)", "capacity": 8})
    default_rooms.append({"id": "غرفة 2 (سعة 7)", "capacity": 7})
    for i in range(1, 14):
        default_rooms.append({"id": f"غرفة {i+2} (سعة 5)", "capacity": 5})
    for i in range(1, 3):
        default_rooms.append({"id": f"غرفة {i+15} (سعة 4)", "capacity": 4})
    st.session_state.hotel_rooms = default_rooms

st.title("🏨 نظام التسكين وإدارة الغرف")

tab1, tab2 = st.tabs(["👥 تسكين النزلاء وحفظ إكسيل", "🛠️ تعديل وإضافة الغرف"])

with tab2:
    st.subheader("إضافة غرفة جديدة")
    new_room_name = st.text_input("اسم أو رقم الغرفة:")
    new_room_beds = st.number_input("عدد السراير:", min_value=1, max_value=50, value=5)
    if st.button("حفظ الغرفة الجديدة"):
        if new_room_name:
            st.session_state.hotel_rooms.append({"id": new_room_name, "capacity": new_room_beds})
            st.success("تم إضافة الغرفة بنجاح")
            st.rerun()

    st.subheader("الغرف الحالية")
    rooms_df = pd.DataFrame(st.session_state.hotel_rooms)
    st.dataframe(rooms_df.rename(columns={"id": "اسم الغرفة", "capacity": "عدد السراير"}), use_container_width=True, hide_index=True)
    
    room_to_delete = st.selectbox("حذف غرفة:", ["-- اختر غرفة لحذفها --"] + [r["id"] for r in st.session_state.hotel_rooms])
    if room_to_delete != "-- اختر غرفة لحذفها --" and st.button("تأكيد الحذف"):
        st.session_state.hotel_rooms = [r for r in st.session_state.hotel_rooms if r["id"] != room_to_delete]
        st.success("تم الحذف")
        st.rerun()

with tab1:
    total_beds = int(pd.DataFrame(st.session_state.hotel_rooms)['capacity'].sum())
    st.info(f"إجمالي السراير المتاحة بالفندق حالياً: {total_beds} سرير")
    guests_input = st.text_area("أدخل أسماء النزلاء (اسم واحد في كل سطر):", height=200)
    
    if guests_input:
        guests = [g.strip() for g in guests_input.replace(",", "\n").split("\n") if g.strip()]
        
        if st.button("🚀 ابدأ التسكين التلقائي", type="primary"):
            sorted_rooms = sorted(st.session_state.hotel_rooms, key=lambda x: x["capacity"], reverse=True)
            room_assignments = {r["id"]: {"capacity": r["capacity"], "guests": []} for r in sorted_rooms}
            
            guest_index = 0
            for room in sorted_rooms:
                r_id = room["id"]
                cap = room["capacity"]
                while len(room_assignments[r_id]["guests"]) < cap and guest_index < len(guests):
                    room_assignments[r_id]["guests"].append(guests[guest_index])
                    guest_index += 1
            
            report_data = []
            for r_id, info in room_assignments.items():
                report_data.append({
                    "اسم الغرفة": r_id,
                    "السراير": info["capacity"],
                    "المسكنين": len(info["guests"]),
                    "الأسماء": ", ".join(info["guests"]) if info["guests"] else "فارغة"
                })
            
            final_df = pd.DataFrame(report_data)
            st.dataframe(final_df, use_container_width=True, hide_index=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False)
            buffer.seek(0)
            
            st.download_button(
                label="📥 تحميل كشف التسكين النهائي (Excel)",
                data=buffer,
                file_name="توزيع_النزلاء.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
