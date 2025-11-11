# Step 6: 마이크로서비스 전환 - 2

> **목표**: API Gateway, Feign Client, Circuit Breaker를 구현하여 마이크로서비스를 완성한다.

---

## 🎯 이 단계를 배우는 이유

### Step 5의 문제점

```
클라이언트가 각 서비스에 직접 접근:
http://localhost:8081/api/users
http://localhost:8082/api/posts
http://localhost:8083/api/comments

문제:
- 클라이언트가 모든 서비스 주소를 알아야 함
- CORS 설정 복잡
- 인증을 각 서비스마다 처리
- 한 서비스 장애 시 전체 시스템 영향
```

### API Gateway의 필요성

```
모든 요청은 API Gateway를 거침:
http://localhost:8080/user-service/api/users
http://localhost:8080/post-service/api/posts
                ↓
          [API Gateway]  ← 단일 진입점
                ↓
    ┌──────────┼──────────┐
[User Service] [Post] [Comment]
```

**프론트엔드 비유**: Nginx, Reverse Proxy
- 프론트엔드에서 `/api/*` 요청을 백엔드로 프록시하는 것과 유사
- API Gateway는 모든 마이크로서비스의 프록시 역할

---

## 💡 핵심 개념

### 1. API Gateway 패턴

#### API Gateway가 하는 일

1. **라우팅**: 요청을 적절한 서비스로 전달
2. **인증/인가**: JWT 토큰 검증 (한 번만)
3. **로드 밸런싱**: 여러 인스턴스에 분산
4. **로깅/모니터링**: 모든 요청 기록
5. **Rate Limiting**: 요청 제한
6. **CORS 처리**: 한 곳에서만 설정

```
[클라이언트]
    ↓
[API Gateway]  ← 모든 처리
    ↓
[마이크로서비스들]  ← 비즈니스 로직만
```

---

### 2. Feign Client (선언적 HTTP 클라이언트)

#### RestTemplate의 불편함

```java
// RestTemplate (Step 5)
String url = "http://user-service/api/users/" + userId;
UserDTO user = restTemplate.getForObject(url, UserDTO.class);

// 매번 URL 조합, 타입 지정, 예외 처리
```

#### Feign Client의 편리함

```java
// Feign Client
@FeignClient(name = "user-service")
public interface UserClient {
    @GetMapping("/api/users/{userId}")
    UserDTO getUser(@PathVariable Long userId);
}

// 사용
UserDTO user = userClient.getUser(userId);  // 끝!
```

**프론트엔드 비유**: Axios, React Query
```javascript
// Axios Instance (프론트)
const api = axios.create({ baseURL: '/api' });
api.get('/users/1');  // 간단!

// Feign Client (백엔드)
userClient.getUser(1L);  // 똑같이 간단!
```

---

### 3. Circuit Breaker (회로 차단기)

#### 문제 상황

```
Post Service → User Service 호출
User Service가 다운되면?
→ Post Service도 타임아웃으로 느려짐
→ 연쇄 장애 (Cascading Failure)
```

#### Circuit Breaker 패턴

```
상태 1: CLOSED (정상)
→ 요청 정상 처리

상태 2: OPEN (장애 감지)
→ 에러율 50% 이상
→ 즉시 실패 반환 (Fallback)
→ User Service 부담 감소

상태 3: HALF_OPEN (복구 시도)
→ 일부 요청만 전달
→ 성공하면 CLOSED로 복귀
```

**프론트엔드 비유**: Error Boundary, Retry Logic
```javascript
// React Error Boundary
<ErrorBoundary fallback={<ErrorMessage />}>
    <UserComponent />
</ErrorBoundary>

// Circuit Breaker도 비슷
// 장애 시 Fallback 반환
```

---

## 🛠️ 최소 구현 코드

### 1. API Gateway 생성

#### 새 프로젝트 생성 (Spring Initializr)
- Dependencies: Gateway, Eureka Discovery Client

#### build.gradle
```gradle
dependencies {
    implementation 'org.springframework.cloud:spring-cloud-starter-gateway'
    implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
}

dependencyManagement {
    imports {
        mavenBom "org.springframework.cloud:spring-cloud-dependencies:2023.0.0"
    }
}
```

#### ApiGatewayApplication.java
```java
package com.project.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient
public class ApiGatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(ApiGatewayApplication.class, args);
    }
}
```

#### application.yml
```yaml
server:
  port: 8080  # 클라이언트는 이 포트로만 접근

spring:
  application:
    name: api-gateway
  
  cloud:
    gateway:
      routes:
        # User Service 라우팅
        - id: user-service
          uri: lb://user-service  # lb = Load Balanced (Eureka 사용)
          predicates:
            - Path=/user-service/**  # 경로가 /user-service로 시작하면
          filters:
            - RewritePath=/user-service/(?<segment>.*), /$\{segment}  # /user-service 제거
        
        # Post Service 라우팅
        - id: post-service
          uri: lb://post-service
          predicates:
            - Path=/post-service/**
          filters:
            - RewritePath=/post-service/(?<segment>.*), /$\{segment}

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
```

**동작 방식**:
```
요청: GET http://localhost:8080/user-service/api/users/1
           ↓
API Gateway: "user-service로 라우팅"
           ↓
Eureka: "user-service는 localhost:8081"
           ↓
실제 호출: GET http://localhost:8081/api/users/1
```

---

### 2. Feign Client 구현

#### Post Service에 의존성 추가

```gradle
dependencies {
    // 기존 의존성들...
    implementation 'org.springframework.cloud:spring-cloud-starter-openfeign'
}
```

#### Feign Client 활성화

```java
// PostServiceApplication.java

@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients  // Feign 활성화
public class PostServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(PostServiceApplication.class, args);
    }
}
```

#### User Client 인터페이스 생성

```java
// com/project/post/client/UserClient.java

package com.project.post.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@FeignClient(name = "user-service")  // Eureka에 등록된 서비스 이름
public interface UserClient {
    
    @GetMapping("/api/users/{userId}")
    UserDTO getUser(@PathVariable Long userId);
}
```

#### DTO 정의

```java
// UserDTO.java (Post Service에 복사)

package com.project.post.dto;

import lombok.Data;

@Data
public class UserDTO {
    private Long id;
    private String name;
    private String email;
}
```

#### Service에서 사용

```java
// PostService.java

@Service
@RequiredArgsConstructor
public class PostService {
    
    private final PostRepository postRepository;
    private final UserClient userClient;  // Feign Client 주입
    
    public PostDTO getPostWithAuthor(Long postId) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new RuntimeException("게시글 없음"));
        
        // Feign Client로 User 정보 가져오기
        UserDTO author = userClient.getUser(post.getAuthorId());
        
        PostDTO dto = PostDTO.from(post);
        dto.setAuthorName(author.getName());
        return dto;
    }
}
```

---

### 3. Circuit Breaker 구현 (Resilience4j)

#### Post Service에 의존성 추가

```gradle
dependencies {
    // 기존 의존성들...
    implementation 'org.springframework.cloud:spring-cloud-starter-circuitbreaker-resilience4j'
}
```

#### application.yml 설정

```yaml
resilience4j:
  circuitbreaker:
    instances:
      userService:  # Circuit Breaker 이름
        register-health-indicator: true
        sliding-window-size: 10  # 최근 10개 요청 기준
        failure-rate-threshold: 50  # 실패율 50% 이상이면 OPEN
        wait-duration-in-open-state: 10s  # OPEN 상태 유지 시간
        permitted-number-of-calls-in-half-open-state: 3  # HALF_OPEN에서 시도 횟수
        automatic-transition-from-open-to-half-open-enabled: true
```

#### Feign Client에 Fallback 추가

```java
// UserClient.java

@FeignClient(
    name = "user-service",
    fallback = UserClientFallback.class  // Fallback 클래스 지정
)
public interface UserClient {
    @GetMapping("/api/users/{userId}")
    UserDTO getUser(@PathVariable Long userId);
}
```

#### Fallback 구현

```java
// UserClientFallback.java

package com.project.post.client;

import com.project.post.dto.UserDTO;
import org.springframework.stereotype.Component;

@Component
public class UserClientFallback implements UserClient {
    
    @Override
    public UserDTO getUser(Long userId) {
        // User Service 장애 시 기본값 반환
        UserDTO defaultUser = new UserDTO();
        defaultUser.setId(userId);
        defaultUser.setName("알 수 없음");  // 기본값
        defaultUser.setEmail("unknown@example.com");
        return defaultUser;
    }
}
```

#### Feign에서 Circuit Breaker 활성화

```yaml
# application.yml

spring:
  cloud:
    openfeign:
      circuitbreaker:
        enabled: true  # Feign에서 Circuit Breaker 사용
```

---

### 4. 전체 흐름

```
[클라이언트]
    ↓
GET http://localhost:8080/post-service/api/posts/1
    ↓
[API Gateway] 라우팅
    ↓
GET http://localhost:8082/api/posts/1
    ↓
[Post Service]
    ↓ userClient.getUser(1)
[Circuit Breaker 체크]
    ↓ User Service 정상?
    ├─ 정상: User Service 호출
    └─ 장애: Fallback 반환 ("알 수 없음")
    ↓
PostDTO 반환 (작성자 정보 포함)
```

---

## 📝 실습 가이드

### Step 1: API Gateway를 통한 호출
```
# API Gateway 통해 User 조회
GET http://localhost:8080/user-service/api/users/1

# API Gateway 통해 Post 조회
GET http://localhost:8080/post-service/api/posts/1
```

### Step 2: Feign Client 테스트
```
# Post 조회 시 작성자 이름 포함되는지 확인
GET http://localhost:8080/post-service/api/posts/1

응답:
{
    "id": 1,
    "title": "제목",
    "authorName": "홍길동"  ← Feign Client로 가져온 정보
}
```

### Step 3: Circuit Breaker 테스트
```
1. User Service 중지
2. Post 조회
GET http://localhost:8080/post-service/api/posts/1

응답:
{
    "id": 1,
    "title": "제목",
    "authorName": "알 수 없음"  ← Fallback 값
}

3. User Service 재시작
4. 다시 조회 → 정상값 반환
```

---

## 🎓 다음 단계로

### 이 단계에서 배운 것
- ✅ API Gateway (Spring Cloud Gateway)
- ✅ Feign Client (선언적 HTTP 클라이언트)
- ✅ Circuit Breaker (Resilience4j)
- ✅ Fallback 처리

### 다음 단계: Step 7 - 이벤트 기반 아키텍처

이제 **동기 통신(HTTP)**에서 **비동기 통신(메시지 큐)**로 전환합니다!

**Step 7에서 배울 것**:
1. **Kafka/RabbitMQ**: 메시지 브로커
2. **이벤트 프로듀서**: 이벤트 발행
3. **이벤트 컨슈머**: 이벤트 구독
4. **Saga 패턴**: 분산 트랜잭션

---

**준비되셨나요? Step 7로 넘어가서 이벤트 기반 아키텍처를 배워봅시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_07_이벤트_기반_아키텍처.md
```

