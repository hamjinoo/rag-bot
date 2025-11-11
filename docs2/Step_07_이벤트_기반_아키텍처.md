# Step 7: 이벤트 기반 아키텍처

> **목표**: 메시지 브로커(Kafka)를 활용한 비동기 이벤트 처리를 구현한다.

---

## 🎯 이 단계를 배우는 이유

### 동기 통신의 한계

```
Post Service → (HTTP) → User Service
              ↓ 대기 (Blocking)
           응답 올 때까지 기다림

문제:
- User Service 느리면 Post Service도 느림
- User Service 장애 시 Post Service 영향
- 실시간 처리 필요 없는 작업도 대기
```

### 비동기 통신의 장점

```
Post Service → [Message Queue] → User Service
              ↓ 즉시 반환
           기다리지 않음

장점:
- 느슨한 결합 (Loose Coupling)
- 장애 격리
- 성능 향상
- 이벤트 재처리 가능
```

### 프론트엔드 비유

```javascript
// 동기 (await)
const user = await fetchUser();  // 기다림
console.log(user);

// 비동기 (Promise)
fetchUser().then(user => console.log(user));  // 기다리지 않음
// 다음 코드 즉시 실행

// 이벤트 (EventEmitter)
eventEmitter.on('userCreated', (user) => {
    console.log('새 사용자:', user);
});
eventEmitter.emit('userCreated', { id: 1, name: '홍길동' });
```

---

## 💡 핵심 개념

### 1. 메시지 브로커 (Message Broker)

#### Kafka vs RabbitMQ

| 특징 | Kafka | RabbitMQ |
|------|-------|----------|
| **목적** | 대용량 스트림 처리 | 일반 메시징 |
| **처리량** | 초당 백만 건 | 초당 수만 건 |
| **사용 사례** | 로그 수집, 이벤트 스트림 | 작업 큐, 알림 |
| **학습 곡선** | 높음 | 낮음 |

**이 가이드에서는 Kafka 사용** (실무에서 더 많이 사용)

---

### 2. Kafka 기본 개념

#### Topic (주제)
- 메시지가 저장되는 카테고리
- 예: `user.created`, `post.created`

#### Producer (생산자)
- 이벤트를 발행하는 서비스
- 예: User Service가 `user.created` 이벤트 발행

#### Consumer (소비자)
- 이벤트를 구독하는 서비스
- 예: Email Service가 `user.created` 이벤트 구독

#### Consumer Group
- 같은 그룹의 Consumer는 메시지를 나눠서 처리
- 예: Email Service 인스턴스 3개 → 부하 분산

```
[User Service] (Producer)
      ↓ user.created 이벤트
[Kafka Topic: user.created]
      ↓
┌─────┴─────┐
[Email]  [Notification]  (Consumers)
```

---

### 3. 이벤트 설계

#### 이벤트 이름 규칙
```
<리소스>.<동작>
user.created
user.updated
post.created
post.deleted
```

#### 이벤트 페이로드
```json
{
    "eventId": "uuid",
    "eventType": "user.created",
    "timestamp": "2024-01-01T10:00:00",
    "data": {
        "userId": 1,
        "name": "홍길동",
        "email": "user@example.com"
    }
}
```

---

## 🛠️ 최소 구현 코드

### 1. Kafka 설치 (Docker)

#### docker-compose.yml
```yaml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

**실행**:
```bash
docker-compose up -d
```

---

### 2. User Service에 Kafka Producer 추가

#### build.gradle
```gradle
dependencies {
    // 기존 의존성들...
    implementation 'org.springframework.kafka:spring-kafka'
}
```

#### application.yml
```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
```

#### 이벤트 DTO
```java
// com/project/user/event/UserCreatedEvent.java

package com.project.user.event;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class UserCreatedEvent {
    private String eventId;
    private String eventType;
    private LocalDateTime timestamp;
    private UserEventData data;
    
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class UserEventData {
        private Long userId;
        private String name;
        private String email;
    }
}
```

#### 이벤트 발행
```java
// com/project/user/service/UserService.java

@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final KafkaTemplate<String, UserCreatedEvent> kafkaTemplate;
    
    public User createUser(User user) {
        // 사용자 저장
        User savedUser = userRepository.save(user);
        
        // 이벤트 발행
        UserCreatedEvent event = new UserCreatedEvent(
            UUID.randomUUID().toString(),
            "user.created",
            LocalDateTime.now(),
            new UserCreatedEvent.UserEventData(
                savedUser.getId(),
                savedUser.getName(),
                savedUser.getEmail()
            )
        );
        
        kafkaTemplate.send("user-events", event);  // Topic: user-events
        
        return savedUser;
    }
}
```

---

### 3. Email Service 생성 (Consumer)

#### 새 프로젝트 생성
- Dependencies: Spring Web, Kafka, Eureka Client

#### application.yml
```yaml
server:
  port: 8084

spring:
  application:
    name: email-service
  
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: email-service-group
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: "*"

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
```

#### 이벤트 리스너
```java
// com/project/email/listener/UserEventListener.java

package com.project.email.listener;

import com.project.email.event.UserCreatedEvent;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class UserEventListener {
    
    @KafkaListener(topics = "user-events", groupId = "email-service-group")
    public void handleUserCreated(UserCreatedEvent event) {
        log.info("User Created Event 수신: {}", event);
        
        // 이메일 발송 로직
        sendWelcomeEmail(event.getData().getEmail(), event.getData().getName());
    }
    
    private void sendWelcomeEmail(String email, String name) {
        log.info("환영 이메일 발송: {} <{}>", name, email);
        // 실제로는 SMTP 서버를 통해 이메일 발송
    }
}
```

---

### 4. Notification Service 추가

#### 이벤트 리스너
```java
// com/project/notification/listener/PostEventListener.java

@Component
@Slf4j
public class PostEventListener {
    
    @KafkaListener(topics = "post-events", groupId = "notification-service-group")
    public void handlePostCreated(PostCreatedEvent event) {
        log.info("Post Created Event 수신: {}", event);
        
        // 알림 발송 로직
        sendNotification(event.getData().getAuthorId(), "새 게시글이 작성되었습니다.");
    }
    
    private void sendNotification(Long userId, String message) {
        log.info("알림 발송 (User {}): {}", userId, message);
        // 실제로는 FCM, 웹소켓 등으로 푸시 알림
    }
}
```

---

### 5. Saga 패턴 (분산 트랜잭션)

#### 문제 상황

```
주문 처리:
1. Order Service: 주문 생성
2. Payment Service: 결제 처리
3. Inventory Service: 재고 차감

만약 3번에서 실패하면?
→ 1, 2번도 취소해야 함 (보상 트랜잭션)
```

#### Choreography Saga (이벤트 기반)

```java
// Order Service
public void createOrder(Order order) {
    order.setStatus(OrderStatus.PENDING);
    orderRepository.save(order);
    
    // 이벤트 발행
    kafkaTemplate.send("order-events", new OrderCreatedEvent(order));
}

// Payment Service
@KafkaListener(topics = "order-events")
public void handleOrderCreated(OrderCreatedEvent event) {
    try {
        processPayment(event.getOrderId());
        kafkaTemplate.send("payment-events", new PaymentSuccessEvent(event.getOrderId()));
    } catch (Exception e) {
        kafkaTemplate.send("payment-events", new PaymentFailedEvent(event.getOrderId()));
    }
}

// Inventory Service
@KafkaListener(topics = "payment-events")
public void handlePaymentSuccess(PaymentSuccessEvent event) {
    try {
        reduceStock(event.getOrderId());
        kafkaTemplate.send("inventory-events", new StockReducedEvent(event.getOrderId()));
    } catch (Exception e) {
        // 보상 트랜잭션: 결제 취소 이벤트 발행
        kafkaTemplate.send("payment-compensation-events", 
                          new RefundPaymentEvent(event.getOrderId()));
    }
}

// Order Service
@KafkaListener(topics = "inventory-events")
public void handleStockReduced(StockReducedEvent event) {
    Order order = orderRepository.findById(event.getOrderId());
    order.setStatus(OrderStatus.COMPLETED);
    orderRepository.save(order);
}
```

---

## 📝 실습 가이드

### Step 1: Kafka 실행
```bash
docker-compose up -d
```

### Step 2: 서비스 실행
1. Eureka Server
2. User Service
3. Email Service
4. Notification Service

### Step 3: 이벤트 발행 테스트
```
POST http://localhost:8081/api/users
{
    "name": "홍길동",
    "email": "user@example.com",
    "password": "password123"
}

콘솔 로그 확인:
[User Service] 사용자 생성
[Email Service] 환영 이메일 발송
```

### Step 4: Kafka Topic 확인
```bash
# Topic 목록
docker exec -it <kafka-container-id> kafka-topics --list --bootstrap-server localhost:9092

# 메시지 확인
docker exec -it <kafka-container-id> kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --from-beginning
```

---

## 🎓 다음 단계로

### 이 단계에서 배운 것
- ✅ Kafka 기본 개념
- ✅ 이벤트 발행 (Producer)
- ✅ 이벤트 구독 (Consumer)
- ✅ Saga 패턴 개념

### 다음 단계: Step 8 - 테스트 및 배포

이제 **테스트 자동화, Docker 컨테이너화, Kubernetes 배포**를 배웁니다!

---

**준비되셨나요? Step 8로 넘어가서 테스트와 배포를 배워봅시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_08_테스트_배포.md
```

