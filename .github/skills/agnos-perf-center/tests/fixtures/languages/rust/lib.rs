// Call-graph fixture, Rust: an inline module, a generic impl block, a trait, an attributed test, a turbofish, a macro.
mod shapes {
    pub struct Square<T> {
        side: T,
    }

    impl<T> Square<T> {
        pub fn new(side: T) -> Self {
            Square { side }
        }
    }

    pub fn convert<U>() -> u8 {
        0
    }

    pub trait Area {
        fn area(&self) -> u8 {
            0
        }
        fn name(&self);
    }

    /// RQ-DEM-001
    #[test]
    fn builds() {
        Square::new(1);
        let n = convert::<u8>();
        println!("{}", n);
    }
}
