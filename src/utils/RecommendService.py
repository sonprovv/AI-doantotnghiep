import math

class RecommendService:
    # Trọng số chỉ dùng cho việc in log (total_score), 
    # việc chọn job sẽ dùng thứ tự ưu tiên (distance -> similarity -> experience)
    DISTANCE_WEIGHT = 1.0
    EXPERIENCE_WEIGHT = 1.0
    SIMILARITY_WEIGHT = 2.0

    # ----------------------------------------------------------

    def haversine_distance_km(self, lat1, lon1, lat2, lon2):
        R = 6371.0  # km

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance_km = R * c
        return distance_km

    # ----------------------------------------------------------

    def build_experience_score(self, experiences):
        experiencesScore = {
            'CLEANING': 2,
            'HEALTHCARE': 2,
            'MAINTENANCE': 2
        }

        check = {
            'CH': False,
            'CM': False,
            'HM': False
        }

        if experiences['CLEANING'] > experiences['HEALTHCARE']:
            check['CH'] = True
        if experiences['CLEANING'] > experiences['MAINTENANCE']:
            check['CM'] = True
        if experiences['HEALTHCARE'] > experiences['MAINTENANCE']:
            check['HM'] = True

        if check['CH'] and check['CM']:
            # CLEANING tốt nhất
            experiencesScore['CLEANING'] = 0
            if check['HM']:
                experiencesScore['HEALTHCARE'] = 1
                experiencesScore['MAINTENANCE'] = 2
            else:
                experiencesScore['HEALTHCARE'] = 2
                experiencesScore['MAINTENANCE'] = 1
        elif not check['CH'] and check['HM']:
            # HEALTHCARE tốt nhất
            experiencesScore['HEALTHCARE'] = 0
            if check['CM']:
                experiencesScore['CLEANING'] = 1
                experiencesScore['MAINTENANCE'] = 2
            else:
                experiencesScore['CLEANING'] = 2
                experiencesScore['MAINTENANCE'] = 1
        elif not check['CM'] and not check['HM']:
            # MAINTENANCE tốt nhất
            experiencesScore['MAINTENANCE'] = 0
            if check['CH']:
                experiencesScore['CLEANING'] = 1
                experiencesScore['HEALTHCARE'] = 2
            else:
                experiencesScore['CLEANING'] = 2
                experiencesScore['HEALTHCARE'] = 1

        return experiencesScore

    # ----------------------------------------------------------

    def recommendJob(self, reference, jobs, top_k=3):
        """
        Ưu tiên:
        1. Gần khách hơn (distance_km thấp hơn)
        2. Giống nội dung query hơn (similarity_penalty thấp hơn => similarity cao hơn)
        3. Phù hợp kinh nghiệm hơn (exp_penalty thấp hơn)
        
        Trả về top_k jobs phù hợp nhất (mặc định 3)
        """
        # Chuẩn hoá location: có thể là dict, string, hoặc thiếu
        raw_location = reference.get('location') if isinstance(reference, dict) else None
        location_name = ""
        clientLat = None
        clientLon = None
        if isinstance(raw_location, dict):
            location_name = raw_location.get('name') or raw_location.get('address') or raw_location.get('formattedAddress') or ""
            clientLat = raw_location.get('lat') or raw_location.get('latitude')
            clientLon = raw_location.get('lon') or raw_location.get('lng') or raw_location.get('longitude')
        elif isinstance(raw_location, str):
            location_name = raw_location
        # Lấy experiences an toàn
        experiences = reference.get('experiences', {'CLEANING': 0, 'HEALTHCARE': 0, 'MAINTENANCE': 0}) if isinstance(reference, dict) else {'CLEANING': 0, 'HEALTHCARE': 0, 'MAINTENANCE': 0}

        # Nếu thiếu toạ độ khách, tạm gán 0 khoảng cách (để không crash). Có thể cải thiện bằng geocoding.
        has_coords = isinstance(clientLat, (int, float)) and isinstance(clientLon, (int, float))

        experiencesScore = self.build_experience_score(experiences)

        # Danh sách để lưu tất cả jobs với key
        job_scores = []

        print("==============================================================")
        print(f"Địa chỉ khách: {location_name}\n")

        for i, job in enumerate(jobs):
            jobLat = job['lat']
            jobLon = job['lon']
            service_type = job['serviceType']

            # 1. khoảng cách
            if has_coords:
                distance_km = self.haversine_distance_km(clientLat, clientLon, jobLat, jobLon)
            else:
                distance_km = 0.0
            distance_score = distance_km * self.DISTANCE_WEIGHT

            # 2. kinh nghiệm
            exp_penalty = experiencesScore.get(service_type, 2) * self.EXPERIENCE_WEIGHT

            # 3. similarity
            sim = job.get("similarity_score", None)
            if sim is None:
                similarity_penalty = 0.0
            else:
                sim_clamped = max(0.0, min(1.0, sim))
                similarity_penalty = (1.0 - sim_clamped) * self.SIMILARITY_WEIGHT

            # tổng để log (không dùng để so sánh ưu tiên chính)
            total_score = distance_score + exp_penalty + similarity_penalty

            print(
                f"[Job {i}] total={total_score:.3f} | "
                f"distance={distance_km:.2f}km | "
                f"sim_penalty={similarity_penalty:.3f} | "
                f"exp_penalty={exp_penalty} | {job.get('location')}"
            )

            # key ưu tiên: Gần hơn -> giống hơn -> hợp kinh nghiệm hơn
            # (càng thấp càng tốt cho cả 3 thành phần)
            key = (round(distance_km, 3), similarity_penalty, exp_penalty)
            
            job_scores.append({
                'index': i,
                'job': job,
                'key': key,
                'total': total_score
            })

        # Sắp xếp theo key (distance -> similarity -> experience)
        job_scores.sort(key=lambda x: x['key'])
        
        # Lấy top_k jobs
        top_jobs = job_scores[:top_k]
        
        print(f"\n=> Chọn top {len(top_jobs)} jobs:")
        for rank, item in enumerate(top_jobs, 1):
            print(f"   {rank}. Job index {item['index']} - key={item['key']}, total={item['total']:.3f}")
        
        # Trả về danh sách top_k jobs
        return [item['job'] for item in top_jobs]