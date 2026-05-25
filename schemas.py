from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=32)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=32)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    category: str
    image_url: str
    stock: int = Field(ge=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: str | None = None
    image_url: str | None = None
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    category: str
    image_url: str | None
    stock: int
    is_active: bool

    class Config:
        from_attributes = True


class CartAdd(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    address: str


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    phone: str
    address: str
    total_price: float
    status: str

    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    id: int
    customer_name: str
    phone: str
    address: str
    total_price: float
    status: str
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str
